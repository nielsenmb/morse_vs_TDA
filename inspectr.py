from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QLabel, QGridLayout, QLineEdit
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from argparse import ArgumentParser
import sys, glob, os
import pandas as pd
import numpy as np

app = None

class MyMainWindow(QMainWindow):
 
    def __init__(self, df, dfpath, image_dir, app, shuffle, initials, cadence):
        super().__init__()
        if shuffle:
            self.df = df.sample(frac=1).reset_index(drop=True)
        else:
            self.df = df

        self.dfpath = dfpath
        self.image_dir = image_dir
        self.app = app
        self.initials = initials
        self.cadence = cadence 
        self.initUI()

    def initUI(self):
        self.resize(1600, 900)
        self.move(50, 50)
        central_widget = MyCentralWidget(self, self.app, self.initials, self.cadence)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('Inspector')
        self.statusBar().showMessage('Waiting...')

    def auto(self):
        self.central_widget.auto()

class MyCentralWidget(QWidget):

    def __init__(self, main_window, app, initials, cadence):
        super().__init__()
        self.main_window = main_window
        self.idx = -1
        self.app = app
        self.initials = initials
        self.cadence = cadence
        self.initUI()

#  "aperiodic", "contact_rot", "dsct_bcep", "eclipse", "gdor_spb", "rrlyr_cepheid", "solarlike", "constant"
    def initUI(self):

        grbox = QGridLayout()

        keys = ['aperiodic', 'contact_rot', 'dsct_bcep', 'eclipse', 'gdor_spb', 'rrlyr_cepheid', 'solarlike', 'constant']
        for i, key in enumerate(keys):
            primary = QPushButton(f'P {key}', self)
            primary.clicked.connect(lambda checked, x=key: self.write_primary(x))
            grbox.addWidget(primary, 0, i)
 
            secondary = QPushButton(f'S {key}', self)
            secondary.clicked.connect(lambda checked, x=key: self.write_secondary(x))
            grbox.addWidget(secondary, 1, i)
        
        # Weirdness line input
        self.line = QLineEdit(self)
        grbox.addWidget(self.line, 0, len(keys)+1)

        # Additional boxes here
        skip_button = QPushButton('Next (&save)', self)
        skip_button.setShortcut('s')
        skip_button.clicked.connect(self.on_skip_button_clicked)
        grbox.addWidget(skip_button, 1, len(keys)+1)


        # define label
        self.label = QLabel(self)
        self.my_widget = MyWidget(self.label, self.main_window.df, self.main_window.image_dir)
 
        # place gridbox and label into vbox
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addLayout(grbox)
        self.setLayout(vbox)
        self.next_image()

    def next_image(self):

        self.idx += 1
        
        while len(self.main_window.df.loc[self.idx, f'Variability_type_WG_{self.cadence}']) > 0:

            self.idx += 1

            if (self.idx in self.main_window.df.index) == False:
                print('Finished going through CSV file')
                print('If any unclassified targets remain, they may not have associated png files')
                sys.exit()

        id = self.main_window.df.loc[self.idx, 'TIC']
 
        if self.cadence == 'lc':
            pathname = os.path.join(*[self.main_window.image_dir, f'{id}.png'])
        elif self.cadence == 'sc':
            pathname = os.path.join(*[self.main_window.image_dir, f'{id}_sc.png'])
        else:
            raise ValueError('cadence must be either lc or sc, default is lc.')
        
        self.psdfile = glob.glob(pathname)
         
        if len(self.psdfile)==0:
            self.my_widget.show_image(os.path.join(*[os.getcwd(),'failed.jpg']))
            mess = f"{os.path.basename(pathname)} not found, so I skipped it"
            print(mess)
            self.write_verdict(mess)
        else:
            self.my_widget.show_image(self.psdfile[0])

    # def on_psd_button_clicked(self):
    #     self.my_widget.show_image(self.psdfile[0])

    # def on_echelle_button_clicked(self):
    #     if len(self.echellefile) == 0:
    #         id = self.main_window.df.loc[self.idx].ID
    #         message = f'No echelle diagram for {id}'
    #         self.main_window.statusBar().showMessage(message)
    #     else:
    #         try:
    #             self.my_widget.show_image(self.echellefile[0])
    #         except:
    #             message = f'Failed to load echelle diagram for {id}'
    #             self.main_window.statusBar().showMessage(message)

 
    def on_skip_button_clicked(self):
        self.assignMulti()
        self.write_verdict('')
        self.line.clear()

    def write_primary(self, classification):
         
        self.main_window.df.at[self.idx, f'Variability_type_WG_{self.cadence}'] = classification.upper()

    def write_secondary(self, classification):
         
        s = self.main_window.df.loc[self.idx, f'Variability_type_extra_{self.cadence}']
        
        prim = self.main_window.df.at[self.idx, f'Variability_type_WG_{self.cadence}']

        if classification.upper() in prim:
            self.main_window.statusBar().showMessage('Secondary cannot be same as primary. No secondary assigment made.')
            print('Secondary cannot be same as primary. No secondary assigment made.')

        if len(prim)>0:
            if (classification.upper() not in s) and (classification.upper() not in prim):
                s += f'+{classification}'
            

            if s.startswith('+'):
                s = s[1:]
            
            self.main_window.df.at[self.idx, f'Variability_type_extra_{self.cadence}'] = s.upper()
        else:
            self.main_window.statusBar().showMessage('Assign primary variability first.')
            print('Assign primary variability first.')
        
      
    
    def assignMulti(self,):
        if len(self.main_window.df.loc[self.idx, f'Variability_type_extra_{self.cadence}']) == 0:
            self.main_window.df.at[self.idx, f'Variability_multi_class_{self.cadence}'] = 0
        else:
            self.main_window.df.at[self.idx, f'Variability_multi_class_{self.cadence}'] = 1
    
 

    def write_verdict(self, mess):
        
        self.main_window.df.at[self.idx, f'TESS_LC_weirdness_{self.cadence}'] = self.line.text()

        self.main_window.df.at[self.idx, 'Vetter_initials'] = self.initials
        
        perc = '%i / %i' % (self.idx+1, len(self.main_window.df))
        
        previous_id = self.main_window.df.loc[self.idx, 'TIC']
         
        self.main_window.statusBar().showMessage(f'Completed {perc} - Previous target was TIC {previous_id} - {mess}')
        
        self.main_window.df.to_csv(self.main_window.dfpath, index=False)

        if self.idx < len(self.main_window.df) - 1:
            self.next_image()
        
        else:
            self.main_window.statusBar().showMessage('Finished')
            sys.exit()

class MyWidget():
    def __init__(self, label, df, image_dir):
        self.label = label

    def show_image(self, sfile):
        pixmap = QPixmap(sfile)
        self.label.setPixmap(pixmap)
        self.label.setScaledContents(True)

def main(df, dfpath, image_dir, shuffle, initials, cadence):
    '''
    app must be defined already!!!
    '''
    global app
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    w = MyMainWindow(df, dfpath, image_dir, app, shuffle, initials, cadence)
 
    w.show()
    app.exit(app.exec_())

parser = ArgumentParser()
parser.add_argument('target_list', type=str)
parser.add_argument('image_dir', type=str)
parser.add_argument('--shuffle', action='store_true', dest='shuffle',
                    help="Shuffle the list of targets. Default is not to shuffle.", default=False)
parser.add_argument('--initials', dest='initials', type=str,
                    help='The initials of the user. Will be added on a per tgt basis.')
parser.add_argument('--cadence', type=str, default='lc')
parser.set_defaults(feature=False)

if __name__ == "__main__":
    args = parser.parse_args()

    conv = {'TIC': str, 
            'Variability_type_WG_lc': str,
            'Variability_multi_class_lc': str,
            'Variability_type_extra_lc': str,
            'TESS_LC_weirdness_lc': str,
            'Variability_type_WG_sc': str,
            'Variability_multi_class_sc': str,	
            'Variability_type_extra_sc': str,	
            'TESS_LC_weirdness_sc': str,
            'Vetter_initials': str,
            }
     
    df = pd.read_csv(args.target_list, converters=conv, delimiter=',')
    if len(df.keys()) == 1:
        df = pd.read_csv(args.target_list, converters=conv, delimiter=';')

    if len(df) > 100:
        sys.setrecursionlimit(len(df))
 
    main(df, args.target_list, args.image_dir, args.shuffle, args.initials, 
         args.cadence)


