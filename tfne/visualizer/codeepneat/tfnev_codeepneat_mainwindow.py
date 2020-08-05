import os
import tempfile
import webbrowser

import matplotlib.pyplot as plt
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

        # Get local temporary directory to save matplotlib created files into
        self.temp_dir = tempfile.gettempdir()

        # Initialize image widgets of all views to refer to them when changing views in order not to create new widgets
        # each time and stack them infinitely
        self.ga_widget_genome_visualization_image = QtSvg.QSvgWidget(self.ga_widget_genome_visualization)
        self.ga_widget_genome_visualization_image.setMaximumHeight(460)
        self.ga_widget_genome_visualization_image.setMaximumWidth(460)

        # Set up sidebar buttons to select the type of analysis. Default activate genome analysis mode
        self.svg_btn_genome_analysis = QtSvg.QSvgWidget(self.centralwidget)
        self.svg_btn_mod_bp_analysis = QtSvg.QSvgWidget(self.centralwidget)
        self.svg_btn_mod_spec_analysis = QtSvg.QSvgWidget(self.centralwidget)
        self.svg_btn_bp_spec_analysis = QtSvg.QSvgWidget(self.centralwidget)
        image_base_dir = os.path.dirname(__file__)
        self.svg_btn_genome_analysis.load(image_base_dir + '/genome_analysis_icon.svg')
        self.svg_btn_mod_bp_analysis.load(image_base_dir + '/module_blueprint_analysis_icon.svg')
        self.svg_btn_mod_spec_analysis.load(image_base_dir + '/module_species_analysis_icon.svg')
        self.svg_btn_bp_spec_analysis.load(image_base_dir + '/blueprint_species_analysis_icon.svg')
        self.svg_btn_genome_analysis.setGeometry(QtCore.QRect(0, 0, 60, 170))
        self.svg_btn_mod_bp_analysis.setGeometry(QtCore.QRect(0, 170, 60, 170))
        self.svg_btn_mod_spec_analysis.setGeometry(QtCore.QRect(0, 340, 60, 170))
        self.svg_btn_bp_spec_analysis.setGeometry(QtCore.QRect(0, 510, 60, 170))
        self.event_svg_btn_genome_analysis()

        # Set layouts
        ga_widget_genome_visualization_layout = QtWidgets.QVBoxLayout(self.ga_widget_genome_visualization)
        ga_widget_genome_visualization_layout.setAlignment(QtCore.Qt.AlignCenter)
        ga_widget_genome_visualization_layout.addWidget(self.ga_widget_genome_visualization_image)

        # Connect Signals
        self.action_documentation.triggered.connect(self.action_documentation_triggered)
        self.action_close.triggered.connect(self.action_close_triggered)
        self.action_exit.triggered.connect(self.action_exit_triggered)
        self.ga_list_generations.itemClicked.connect(self.click_ga_list_generations)
        self.svg_btn_genome_analysis.mousePressEvent = self.event_svg_btn_genome_analysis
        self.svg_btn_mod_bp_analysis.mousePressEvent = self.event_svg_btn_module_blueprint_analysis

    def event_svg_btn_genome_analysis(self, *args, **kwargs):
        """"""
        # Set Color focus on Genome Analysis
        svg_btn_genome_analysis_bg = QtGui.QPalette(self.svg_btn_genome_analysis.palette())
        svg_btn_genome_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('gray'))
        self.svg_btn_genome_analysis.setPalette(svg_btn_genome_analysis_bg)
        self.svg_btn_genome_analysis.setAutoFillBackground(True)
        svg_btn_mod_bp_analysis_bg = QtGui.QPalette(self.svg_btn_mod_bp_analysis.palette())
        svg_btn_mod_bp_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_mod_bp_analysis.setPalette(svg_btn_mod_bp_analysis_bg)
        self.svg_btn_mod_bp_analysis.setAutoFillBackground(True)
        svg_btn_mod_spec_analysis_bg = QtGui.QPalette(self.svg_btn_mod_spec_analysis.palette())
        svg_btn_mod_spec_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_mod_spec_analysis.setPalette(svg_btn_mod_spec_analysis_bg)
        self.svg_btn_mod_spec_analysis.setAutoFillBackground(True)
        svg_btn_bp_spec_analysis_bg = QtGui.QPalette(self.svg_btn_bp_spec_analysis.palette())
        svg_btn_bp_spec_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_bp_spec_analysis.setPalette(svg_btn_bp_spec_analysis_bg)
        self.svg_btn_bp_spec_analysis.setAutoFillBackground(True)

        # Activate genome analysis mode, deactivate other modes
        self.widget_genome_analysis.show()
        self.widget_mod_bp_analysis.close()

        # Create graph showing the best genome fitness over the generations and display it
        x_axis_generations = sorted(self.tfne_state_backups.keys())
        y_axis_fitness = list()
        for gen in x_axis_generations:
            y_axis_fitness.append(self.tfne_state_backups[gen].best_fitness)
        plt.plot(x_axis_generations, y_axis_fitness)
        plt.ylabel('best fitness')
        plt.xlabel('generation')
        plt.savefig(self.temp_dir + '/best_genome_fitness_analysis.svg')
        self.svg_best_genome_analysis = QtSvg.QSvgWidget(self.widget_genome_analysis)
        self.svg_best_genome_analysis.load(self.temp_dir + '/best_genome_fitness_analysis.svg')
        self.svg_best_genome_analysis.setGeometry(QtCore.QRect(10, 0, 440, 320))

        # Create strings that are displayed in the list of best genomes
        best_genome_in_gen_list = list()
        for gen in x_axis_generations:
            best_genome_id = self.tfne_state_backups[gen].best_genome.get_id()
            best_genome_in_gen_list.append(f'Generation {gen} - Genome #{best_genome_id}')
        self.ga_list_generations.clear()
        self.ga_list_generations.addItems(best_genome_in_gen_list)

    def event_svg_btn_module_blueprint_analysis(self, *args, **kwargs):
        """"""
        # Set Color focus on Genome Analysis
        svg_btn_genome_analysis_bg = QtGui.QPalette(self.svg_btn_genome_analysis.palette())
        svg_btn_genome_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_genome_analysis.setPalette(svg_btn_genome_analysis_bg)
        self.svg_btn_genome_analysis.setAutoFillBackground(True)
        svg_btn_mod_bp_analysis_bg = QtGui.QPalette(self.svg_btn_mod_bp_analysis.palette())
        svg_btn_mod_bp_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('gray'))
        self.svg_btn_mod_bp_analysis.setPalette(svg_btn_mod_bp_analysis_bg)
        self.svg_btn_mod_bp_analysis.setAutoFillBackground(True)
        svg_btn_mod_spec_analysis_bg = QtGui.QPalette(self.svg_btn_mod_spec_analysis.palette())
        svg_btn_mod_spec_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_mod_spec_analysis.setPalette(svg_btn_mod_spec_analysis_bg)
        self.svg_btn_mod_spec_analysis.setAutoFillBackground(True)
        svg_btn_bp_spec_analysis_bg = QtGui.QPalette(self.svg_btn_bp_spec_analysis.palette())
        svg_btn_bp_spec_analysis_bg.setColor(QtGui.QPalette.Window, QtGui.QColor('darkGray'))
        self.svg_btn_bp_spec_analysis.setPalette(svg_btn_bp_spec_analysis_bg)
        self.svg_btn_bp_spec_analysis.setAutoFillBackground(True)

        # Activate genome analysis mode, deactivate other modes
        self.widget_genome_analysis.close()
        self.widget_mod_bp_analysis.show()

        # TODO Create rest of the widgets for the rest of the analysis window
        pass

    def click_ga_list_generations(self, item):
        """"""
        # Determine selected best genome
        item_text = item.text()
        chosen_gen = int(item_text[11:(item_text.find('-', 13) - 1)])
        best_genome = self.tfne_state_backups[chosen_gen].best_genome

        # create visualization of best genome and show in image widget
        best_genome_plot_path = best_genome.visualize(show=False,
                                                      save_dir_path=self.temp_dir,
                                                      show_shapes=True,
                                                      show_layer_names=False)
        self.ga_widget_genome_visualization_image.close()
        self.ga_widget_genome_visualization_image.load(best_genome_plot_path)
        self.ga_widget_genome_visualization_image.show()

        # Update genome info labels to show genome information
        mod_spec_to_mod_id = dict()
        for mod_spec, mod in best_genome.bp_assigned_modules.items():
            mod_spec_to_mod_id[mod_spec] = mod.module_id
        self.ga_lbl_genome_id.setText(f'Genome ID {best_genome.genome_id}')
        self.ga_lbl_genome_fitness_value.setText(str(best_genome.fitness))
        self.ga_lbl_genome_bp_id_value.setText(str(best_genome.blueprint.blueprint_id))
        self.ga_lbl_genome_assign_mod_value.setText(str(mod_spec_to_mod_id))
        self.ga_lbl_genome_out_layers_value.setText(str(best_genome.output_layers))
        self.ga_lbl_genome_input_shape_value.setText(str(best_genome.input_shape))
        self.ga_lbl_genome_dtype_value.setText(str(best_genome.dtype))
        self.ga_lbl_genome_orig_gen_value.setText(str(best_genome.origin_generation))

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
