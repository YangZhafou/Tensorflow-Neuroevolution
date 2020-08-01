import webbrowser

from PyQt5 import QtCore, QtWidgets, QtGui, QtSvg

from .tfnev_codeepneat_mainwindow_ui import Ui_MainWindow


class TFNEVCoDeepNEATMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """"""

    def __init__(self, tfne_state_backups, parent_window, *args, **kwargs):
        """"""
        super(TFNEVCoDeepNEATMainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Register parameters
        self.tfne_state_backups = tfne_state_backups
        self.parent_window = parent_window

        # Connect Signals
        self.action_documentation.triggered.connect(self.action_documentation_triggered)
        self.action_close.triggered.connect(self.action_close_triggered)
        self.action_exit.triggered.connect(self.action_exit_triggered)

    def action_close_triggered(self):
        """"""
        self.parent_window.show()
        self.destroy()

    def action_exit_triggered(self):
        """"""
        self.parent_window.destroy()
        self.destroy()
        exit()

    @staticmethod
    def action_documentation_triggered():
        """"""
        webbrowser.open('https://tfne.readthedocs.io')

    '''
        # Set up buttons for the type of analysis (genome or species analysis) and activate genome analysis mode
        self.svg_btn_genomes = QtSvg.QSvgWidget(self)
        self.svg_btn_genomes.load('./tfnev_mainwindow/genome_analysis_icon.svg')
        self.svg_btn_genomes.setGeometry(QtCore.QRect(0, 20, 50, 340))
        self.svg_btn_species = QtSvg.QSvgWidget(self)
        self.svg_btn_species.load('./tfnev_mainwindow/species_analysis_icon.svg')
        self.svg_btn_species.setGeometry(QtCore.QRect(0, 360, 50, 340))
        self.svg_btn_genomes_event()

        # Set up Genome placeholder image
        self.svg_genome_placeholder = QtSvg.QSvgWidget(self.centralwidget_genome)
        self.svg_genome_placeholder.load('./tfnev_mainwindow/genome_placeholder_icon.svg')
        self.svg_genome_placeholder.setGeometry(QtCore.QRect(520, 10, 400, 400))

        # Connect Signals
        self.list_generations.itemClicked.connect(self.list_generations_click)
        self.list_genomes.itemClicked.connect(self.list_genomes_click)
        self.action_documentation.triggered.connect(self.action_documentation_triggered)
        self.action_close.triggered.connect(self.action_close_triggered)
        self.action_exit.triggered.connect(self.action_exit_triggered)
        self.svg_btn_genomes.mousePressEvent = self.svg_btn_genomes_event
        self.svg_btn_species.mousePressEvent = self.svg_btn_species_event

        # Register parameters and load files from chosen directory
        self.run_data = dict()
        self.list_generations_dict = dict()
        self.present_modules_dict = dict()
        self.present_blueprints_dict = dict()
        self.backup_dir_path = backup_dir_path
        self.parent_window = parent_window
        self.load_backup()

    def load_backup(self):
        for tfne_run_backup_file in os.listdir(self.backup_dir_path):
            tfne_run_backup_path = self.backup_dir_path + '/' + tfne_run_backup_file
            with open(tfne_run_backup_path) as tfne_run_backup:
                temp_run_data = json.load(tfne_run_backup)
                generation = temp_run_data['generation_counter']
                self.run_data[generation] = temp_run_data
                self.list_generations_dict[f'Generation {generation}'] = generation

        list_generations_dict_sorted = sorted(self.list_generations_dict.keys(),
                                              key=self.list_generations_dict.get)
        self.list_generations.addItems(list_generations_dict_sorted)

    def list_generations_click(self, item):
        self.list_genomes.clear()

        self.chosen_gen = self.list_generations_dict[item.text()]

        present_module_ids = self.run_data[self.chosen_gen]['modules'].keys()
        for present_mod_id in present_module_ids:
            self.present_modules_dict[f'Module {present_mod_id}'] = present_mod_id
        self.list_genomes.addItems(self.present_modules_dict.keys())

        present_blueprint_ids = self.run_data[self.chosen_gen]['blueprints'].keys()
        for present_bp_id in present_blueprint_ids:
            self.present_blueprints_dict[f'Blueprint {present_bp_id}'] = present_bp_id
        self.list_genomes.addItems(self.present_blueprints_dict.keys())

        lbl_info = "mod_species: " + str(self.run_data[self.chosen_gen]['mod_species']) + "\n" + \
                   "mod_species_repr: " + str(self.run_data[self.chosen_gen]['mod_species_repr']) + "\n" + \
                   "mod_species_fitness_history: " + str(
            self.run_data[self.chosen_gen]['mod_species_fitness_history']) + "\n" + \
                   "mod_species_counter: " + str(self.run_data[self.chosen_gen]['mod_species_counter']) + "\n" + \
                   "bp_species: " + str(self.run_data[self.chosen_gen]['bp_species']) + "\n" + \
                   "bp_species_repr: " + str(self.run_data[self.chosen_gen]['bp_species_repr']) + "\n" + \
                   "bp_species_fitness_history: " + str(
            self.run_data[self.chosen_gen]['bp_species_fitness_history']) + "\n" + \
                   "bp_species_counter: " + str(self.run_data[self.chosen_gen]['bp_species_counter']) + "\n" + \
                   "best_genome: " + str(self.run_data[self.chosen_gen]['best_genome'])
        self.lbl_generation_info.setGeometry(QtCore.QRect(60, 330, 380, 300))
        self.lbl_generation_info.setText(lbl_info)

    def list_genomes_click(self, item):
        self.lbl_genome_info.setGeometry(QtCore.QRect(460, 430, 530, 300))
        self.lbl_genome_info.setText("")

        if item.text() in self.present_modules_dict:
            chosen_id = self.present_modules_dict[item.text()]
            lbl_info = "Module Genotype: " + str(self.run_data[self.chosen_gen]['modules'][chosen_id])
            self.lbl_genome_info.setText(lbl_info)
        elif item.text() in self.present_blueprints_dict:
            chosen_id = self.present_blueprints_dict[item.text()]
            lbl_info = "Blueprint Genotype: " + str(self.run_data[self.chosen_gen]['blueprints'][chosen_id])
            self.lbl_genome_info.setText(lbl_info)

    def svg_btn_genomes_event(self, *args, **kwargs):
        # Set Color focus on Genome Analysis
        svg_btn_genomes_bg = QtGui.QPalette(self.svg_btn_genomes.palette())
        svg_btn_genomes_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('gray'))
        self.svg_btn_genomes.setPalette(svg_btn_genomes_bg)
        self.svg_btn_genomes.setAutoFillBackground(True)
        svg_btn_species_bg = QtGui.QPalette(self.svg_btn_species.palette())
        svg_btn_species_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_species.setPalette(svg_btn_species_bg)
        self.svg_btn_species.setAutoFillBackground(True)

        # Activate Genome Analysis Mode
        self.centralwidget_genome.show()

    def svg_btn_species_event(self, *args, **kwargs):
        # Set Color focus on Species Analysis
        svg_btn_genomes_bg = QtGui.QPalette(self.svg_btn_genomes.palette())
        svg_btn_genomes_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_genomes.setPalette(svg_btn_genomes_bg)
        self.svg_btn_genomes.setAutoFillBackground(True)
        svg_btn_species_bg = QtGui.QPalette(self.svg_btn_species.palette())
        svg_btn_species_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('gray'))
        self.svg_btn_species.setPalette(svg_btn_species_bg)
        self.svg_btn_species.setAutoFillBackground(True)

        # Activate Species Analysis Mode
        self.centralwidget_genome.hide()
    '''
