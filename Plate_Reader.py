
import matplotlib
import numpy as np
from scipy import stats as sci
from openpyxl import load_workbook
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import string


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())





class PlateReaderExcelData:
    def __init__(self, index, sample, od):
        self.index = index
        self.sample = sample
        self.od = od


class OmegaDataReader:
    def __init__(self, filename):
        workbook = load_workbook(filename, read_only=True)

        worksheet = workbook['All Intervals']

        data_rows = list()

        self.time = list()
        time_columns = list()
        for row in worksheet.rows:
            if row[2].value == 'Time':
                for cell in row[3:]:
                    time_string = str(cell.value).split()
                    if len(time_string) == 2:
                        current_time = float(time_string[0])

                    elif len(time_string) == 4:
                        current_time = float(time_string[0]) + float(time_string[2]) / 60
                    else:
                        current_time = None

                    if current_time is not None and current_time not in self.time:
                        self.time.append(current_time)
                        time_columns.append(cell.column)

                data_range = max(time_columns) - min(time_columns)


            if len(str(row[0].value)) == 1:
                data_rows.append(row)

        data_min = 4 + data_range
        data_max = 5 + data_range * 2

        plate_reader_class_list = list()
        for row in data_rows:
            blank_corrected_data = list()
            plate_index = [str(row[0].value), str(row[1].value)]
            sample = str(row[2].value).split()[1]

            data_raw = row[data_min:data_max]
            for cell in data_raw:
                blank_corrected_data.append(cell.value)
            plate_reader_class_list.append(PlateReaderExcelData(plate_index, sample, blank_corrected_data))

        self.model_list = list()
        self.od_list = list()
        for x in range(0, 7):
            column = list()
            od_column = list()
            for y in range(0, 12):
                column.append("x")
                od_column.append(" ")
            self.model_list.append(column)
            self.od_list.append(od_column)

        plate_plan_dict = {'A': '0', 'B': '1', 'C': '2', 'D': '3', 'E': '4', 'F': '5', 'G': '6', 'H': '7'}
        for data in plate_reader_class_list:
            if data.sample == 'B':
                self.model_list[int(plate_plan_dict[data.index[0]])][int(data.index[1])] = "B"
            else:
                self.model_list[int(plate_plan_dict[data.index[0]])][int(data.index[1])] = " "
                self.od_list[int(plate_plan_dict[data.index[0]])][int(data.index[1])] = data.od

    def get_od_list(self):
        return self.od_list

    def get_model_list(self):
        return self.model_list

    def get_time(self):
        return self.time


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=10, height=10, dpi=100):
        self.press = None
        self.prevX = 0
        self.ydata = list()
        self.xdata = list()
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        self.axes.hold(True)

        #self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        FigureCanvas.mpl_connect(self,'button_press_event', self.onclick)
        FigureCanvas.mpl_connect(self, 'button_release_event', self.onrelease)
        FigureCanvas.mpl_connect(self, 'motion_notify_event', self.onmove)
        FigureCanvas.mpl_connect(self, 'scroll_event', self.zoom)
        FigureCanvas.mpl_connect(self, 'pick_event', self.onpick)
        FigureCanvas.mpl_connect(self, 'figure_enter_event', self.on_enter)
        FigureCanvas.mpl_connect(self, 'figure_exit_event', self.on_exit)

    def compute_initial_figure(self):
        pass

    def onclick(self,event):
        pass

    def onpick(self,event):
        pass

    def onmove(self,event):
        pass

    def onrelease(self, event):
        pass

    def scroll(self,event):
        pass

    def on_enter(self,event):
        pass

    def on_exit(self,event):
        pass

    def zoom(self,event):
        pass

class PlateReaderGraphLine():
    def __init__(self, linenum, line_data, mean, std, line_col, line_style, marker, legend):
        self.line_num = linenum
        self.line_data = line_data
        self.mean = mean
        self.std = std
        self.line_col = line_col
        self.line_style = line_style
        self.marker = marker
        self.legend = legend


class PlateReaderGraph(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self,  *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

        self.data_line_list = list()
        self.data_line_num = 0
        self.text_list= list()

        self.harmonics = []
        self.overline = False
        self.active = True
        self.legend = None


    def plot_figure(self,time,data, line_num, line_col, line_style, marker, legend, error_type):
        self.time = time
        legend_pos = False

        for index, line in enumerate(self.data_line_list):
            if line.line_num == line_num:
                self.data_line_list.pop(index)

        try:
            legend_pos = self.legend._loc
        except AttributeError:
            print("Legend Not Set Yet")


        data_array = np.asarray(data)

        mean_array = np.mean(data_array, axis =0)
        std_array = self.calculate_error(data_array,error_type)
        self.data_line_list.insert(line_num,PlateReaderGraphLine(line_num, data_array,mean_array, std_array,line_col, line_style, marker, legend))
        self.axes.cla()
        legends = list()
        for line in self.data_line_list:
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col, linestyle= line.line_style, marker=line.marker)
            legends.append(line.legend)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        if legend_pos:
            self.legend._loc = legend_pos
        self.draw()

    def clear_line(self, line_num):
        self.data_line_list.pop(line_num)
        legend_pos = self.legend._loc
        self.axes.cla()
        legends = list()
        for line in self.data_line_list:
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col, linestyle=line.line_style, marker=line.marker)
            legends.append(line.legend)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        self.legend._loc = legend_pos
        self.draw()

    def set_line_colour(self, line_num, line_col):
        legend_pos = self.legend._loc
        self.axes.cla()
        legends = list()
        for line in self.data_line_list:
            if int(line.line_num) == int(line_num):
                line.line_col = line_col
            legends.append(line.legend)
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col, linestyle= line.line_style, marker=line.marker)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        self.legend._loc = legend_pos
        self.draw()

    def set_line_style(self, line_num, line_style):
        legend_pos = self.legend._loc
        self.axes.cla()
        legends = list()
        for line in self.data_line_list:
            if int(line.line_num) == int(line_num):
                line.line_style = line_style
            legends.append(line.legend)
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col, linestyle= line.line_style, marker=line.marker)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        self.legend._loc = legend_pos
        self.draw()

    def set_line_marker(self, line_num, marker):
        legend_pos = self.legend._loc
        self.axes.cla()
        legends = list()
        for line in self.data_line_list:
            if int(line.line_num) == int(line_num):
                line.marker = marker
            legends.append(line.legend)
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col, linestyle=line.line_style, marker=line.marker)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        self.legend._loc = legend_pos
        self.draw()

    def set_line_legend(self, line_num, legend):
        legend_pos = self.legend._loc
        self.axes.cla()
        legends =list()
        for line in self.data_line_list:
            if int(line.line_num) == int(line_num):
                line.legend = legend
            legends.append(line.legend)
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col,
                                          linestyle=line.line_style, marker=line.marker)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        self.legend._loc = legend_pos
        self.draw()

    def clear_figure(self):
        self.axes.cla()
        self.data_line_list= list()

        self.data_line_num = 0
        self.text_list = list()

    def set_error(self, error_type):
        legend_pos = self.legend._loc
        print("Set Error")
        self.axes.cla()
        legends = list()
        for line in self.data_line_list:
            line.std = self.calculate_error(line.line_data, error_type)
            legends.append(line.legend)
            self.plt = self.axes.errorbar(self.time, line.mean, line.std, color=line.line_col,
                                          linestyle=line.line_style, marker=line.marker)
        self.legend = self.axes.legend(legends)
        self.legend.draggable()
        self.legend._loc = legend_pos
        self.draw()

    def calculate_error(self, data, error_type):
        if error_type == 0:
            error = None
        elif error_type == 1:
            error = np.std(data, axis=0)
        elif error_type == 2:
            error = sci.sem(data)
        return error


    def get_current_plot(self):
        return self.axes




class PlateReaderData:
    def __init__(self):
        row = list()
        selected_row = list()
        table_whitespace = list()
        data= list()


        for x in range(0, 7):
            row = list()
            data_row = list()
            for x in range(0,12):
                row.append("")
                data_row.append(np.random.random([20]))

            table_whitespace.append(row)
            data.append(data_row)
        time = np.linspace(0,20,20)
        self.table_data = [table_whitespace,time,data]

    def get_table_data(self):
        return self.table_data


class PlateReaderGraphEditor(QtWidgets.QVBoxLayout):

    def __init__(self, graph):
        super(PlateReaderGraphEditor,self).__init__()
        self.graph = graph
        title_box = QtWidgets.QHBoxLayout()
        xaxis_box = QtWidgets.QHBoxLayout()
        yaxis_box = QtWidgets.QHBoxLayout()

        title_text = QtWidgets.QLabel("Title: ")
        xaxis_text = QtWidgets.QLabel("X Axis: ")
        yaxis_text = QtWidgets.QLabel("Y Axis: ")

        self.error_button_group = QtWidgets.QButtonGroup()
        self.error_button_group.buttonClicked[int].connect(self.set_error)
        noerror_button = QtWidgets.QRadioButton("None")
        stdev_button =QtWidgets.QRadioButton("Std Dev")
        stderr_button = QtWidgets.QRadioButton("Std Error")
        stdev_button.setChecked(True)

        self.error_button_group.addButton(noerror_button, 0)
        self.error_button_group.addButton(stdev_button, 1)
        self.error_button_group.addButton(stderr_button,2)

        self.error_button_groupbox = QtWidgets.QGroupBox("Error")

        self.error_hbox = QtWidgets.QHBoxLayout()
        self.error_hbox.addWidget(noerror_button)
        self.error_hbox.addWidget(stdev_button)
        self.error_hbox.addWidget(stderr_button)

        self.error_button_groupbox.setLayout(self.error_hbox)

        self.title_edit = QtWidgets.QLineEdit()
        self.xaxis_edit = QtWidgets.QLineEdit()
        self.yaxis_edit = QtWidgets.QLineEdit()

        self.title_edit.textChanged.connect(self.set_title)
        self.xaxis_edit.textChanged.connect(self.set_xaxis)
        self.yaxis_edit.textChanged.connect(self.set_yaxis)

        title_box.addWidget(title_text)
        title_box.addWidget(self.title_edit)

        xaxis_box.addWidget(xaxis_text)
        xaxis_box.addWidget(self.xaxis_edit)

        yaxis_box.addWidget(yaxis_text)
        yaxis_box.addWidget(self.yaxis_edit)

        self.addLayout(title_box)
        self.addLayout(xaxis_box)
        self.addLayout(yaxis_box)
        self.addWidget(self.error_button_groupbox)

    def set_title(self):
        new_text = self.title_edit.text()
        self.graph.get_current_plot().set_title(new_text)
        self.graph.draw()

    def set_xaxis(self):
        new_text = self.xaxis_edit.text()
        try:
            self.graph.get_current_plot().set_xlabel(new_text)
        except ValueError:
            print("Having Some Problems With Text")
        self.graph.draw()

    def set_yaxis(self):
        new_text = self.yaxis_edit.text()
        try:
            self.graph.get_current_plot().set_ylabel(new_text)
        except ValueError:
            print("Having Some Problems With Text")
        self.graph.draw()

    def set_error(self, selected_id):
        self.graph.set_error(selected_id)
    def get_checked_error(self):
        return self.error_button_group.checkedId()

class PlateReaderLine(QtWidgets.QWidget):
    def __init__(self, line_num, graph):
        super(PlateReaderLine, self).__init__()
        self.line_num = line_num
        self.graph = graph
        self.colour_dict = {'Blue':'b', 'Red': 'r', 'Green': 'g', 'Black':'k'}
        self.marker_dict = {'None':'None', 'Square': "s", 'Circle':'o', 'Triangle':'^'}


        self.legend_edit = QtWidgets.QLineEdit(str(line_num))
        self.legend_edit.textChanged.connect(self.set_legend)
        self.num_label = QtWidgets.QLabel(str(line_num))
        line_col_label = QtWidgets.QLabel("Line Colour")
        line_style_label = QtWidgets.QLabel("Line Style")
        line_marker_label = QtWidgets.QLabel("Marker")

        self.line_col_box = QtWidgets.QComboBox()
        self.line_col_box.addItems(['Blue', 'Green', 'Red', 'Black'])
        self.line_col_box.currentIndexChanged.connect(self.set_col)

        self.line_style_box = QtWidgets.QComboBox()
        self.line_style_box.addItems(['-', '--','-.',':'])
        self.line_style_box.currentIndexChanged.connect(self.set_style)

        self.line_marker_box = QtWidgets.QComboBox()
        self.line_marker_box.addItems(['None', 'Square', 'Circle', 'Triangle'])
        self.line_marker_box.currentIndexChanged.connect(self.set_marker)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        hbox.addWidget(self.legend_edit)
        hbox.addWidget(self.num_label)
        hbox.addWidget(line_col_label)
        hbox.addWidget(self.line_col_box)
        hbox.addWidget(line_style_label)
        hbox.addWidget(self.line_style_box)
        hbox.addWidget(line_marker_label)
        hbox.addWidget(self.line_marker_box)

        self.setLayout(hbox)

    def get_line_num(self):
        return self.line_num

    def get_line_col(self):
        colour = self.line_col_box.currentText()
        return self.colour_dict[colour]

    def get_line_style(self):
        return self.line_style_box.currentText()

    def get_line_marker(self):
        marker = self.line_marker_box.currentText()
        return self.marker_dict[marker]

    def get_line_legend(self):
        legend = self.legend_edit.text()
        return legend

    def set_marker(self):
        marker = self.line_marker_box.currentText()
        marker_val = self.marker_dict[marker]
        self.graph.set_line_marker(self.get_line_num(), marker_val)

    def set_col(self):
        colour = self.line_col_box.currentText()
        colour_val = self.colour_dict[colour]
        self.graph.set_line_colour(self.get_line_num(),colour_val)

    def set_style(self):
        style = self.line_style_box.currentText()
        self.graph.set_line_style(self.get_line_num(), style)

    def set_legend(self):
        legend = self.legend_edit.text()
        self.graph.set_line_legend(self.get_line_num(),legend)


class MyWindow(QtWidgets.QWidget):
    def __init__(self, *args):
        QtWidgets.QWidget.__init__(self, *args)

        self.current_line_indexes = list()
        self.line_count = 0
        # create table
        self.get_table_data()
        data_reader = OmegaDataReader('PlateReaderResults.xlsx')
        model_view = data_reader.get_model_list()
        plate_data = data_reader.get_od_list()
        time = data_reader.get_time()
        self.tabledata = [model_view, time, plate_data]
        header = self.createTableHeader()
        self.tablemodel = PlateReaderTableModel(self.tabledata, header, self)
        self.tableview = PlateReaderTableView(self.tablemodel)
        # layout
        layout = QtWidgets.QVBoxLayout()
        main_box =QtWidgets.QHBoxLayout()
        self.line_list = QtWidgets.QListWidget()
        self.line_list.itemClicked.connect(self.line_selected)
        add_line_button = QtWidgets.QPushButton("Add Line")
        add_line_button.clicked.connect(self.add_line)
        set_data_line_button = QtWidgets.QPushButton("Set Data")
        set_data_line_button.clicked.connect(self.set_data_line)
        clear_cells_button = QtWidgets.QPushButton("Clear Line")
        clear_cells_button.clicked.connect(self.clear_line)
        layout.addWidget(self.tableview)
        layout.addWidget(self.line_list)
        layout.addWidget(add_line_button)
        layout.addWidget(set_data_line_button)
        layout.addWidget(clear_cells_button)
        main_box.addLayout(layout)
        self.graph = PlateReaderGraph()
        self.graph_editor = PlateReaderGraphEditor(self.graph)
        tab = QtWidgets.QTabWidget()
        tab.addTab(self.graph, "Graph 1")
        main_box.addWidget(tab)
        main_box.addLayout(self.graph_editor)
        self.setLayout(main_box)



    def set_data_line(self):
        indexes = self.tableview.selectionModel().selectedIndexes()
        line_data = list()
        try:
            selected_list_index = self.line_list.selectionModel().selectedIndexes()[0].row()
        except IndexError:
            print("Please select a line")
            return
        print("Selected Index: " + str(selected_list_index))
        item = self.line_list.item(selected_list_index)
        line_item = self.line_list.itemWidget(item)
        self.clear_cells(selected_list_index)
        for index in indexes:

            self.tablemodel.setData(index, line_item.get_line_num())
            self.tableview.selectionModel().select(index, QtCore.QItemSelectionModel.Deselect)
            line_data.append(self.tablemodel.get_graph_data(index))
        self.current_line_indexes[selected_list_index] = indexes

        try:
            invalid = 0
            for index, data in enumerate(line_data):
                if data is None:
                    line_data.pop(index)
                    invalid +=1
            if invalid > 0:
                print("Removed " + str(invalid) + " invalid data selections")
        except TypeError:
            print("Please select some data points!")
            line_data = []
        if line_data:
            self.graph.plot_figure(self.tablemodel.time, line_data, int(line_item.get_line_num()),line_item.get_line_col(),
                                   line_item.get_line_style(), line_item.get_line_marker(), line_item.get_line_legend(),
                                    self.graph_editor.get_checked_error())

    def clear_cells(self, index):
        current_line = self.current_line_indexes[index]
        if not current_line:
            print(self.current_line_indexes[index])
            pass
        else:
            for index in current_line:
                self.tablemodel.setData(index, "")

    def clear_line(self):
        indexes = self.tableview.selectionModel().selectedIndexes()
        selected_list_index = self.line_list.selectionModel().selectedIndexes()[0].row()
        self.clear_cells(selected_list_index)
        for index in indexes:
            self.tablemodel.setData(index, "")
            self.tableview.selectionModel().select(index, QtCore.QItemSelectionModel.Deselect)
        self.graph.clear_line(selected_list_index)

    def add_line(self):
        self.line_count +=1
        line = PlateReaderLine(self.line_count, self.graph)
        item = QtWidgets.QListWidgetItem()
        item.setSizeHint(line.sizeHint())
        self.line_list.addItem(item)
        self.line_list.setItemWidget(item, line)
        self.line_list.item(self.line_count -1).setSelected(True)
        self.line_list.setFocus()
        self.current_line_indexes.append([])

    def line_selected(self):
        print(len(self.line_list.selectedItems()))
        self.tableview.set_current_line(self.line_list.selectedItems()[0].text())

    def get_table_data(self):

        self.tabledata = PlateReaderData().get_table_data()
        print(len(self.tabledata))
        print(len(self.tabledata[0]))

    def createTableHeader(self):

        header_col = list()
        # set the table model
        for x in range(1,13):
            header_col.append(str(x))
        header_row = string.ascii_uppercase[:7]
        header = [header_col,header_row]

        return header




class PlateReaderTableView(QtWidgets.QTableView):
    def __init__(self, model):
        QtWidgets.QTableView.__init__(self)
        self.setModel(model)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.current_line = ""

        # set the minimum size
        self.setMinimumSize(600, 300)

        # hide grid
        self.setShowGrid(False)

        # set the font
        font = QtGui.QFont("Courier New", 8)
        self.setFont(font)

        # hide vertical header
        vh = self.verticalHeader()
        vh.setVisible(True)

        # set horizontal header properties
        hh = self.horizontalHeader()
        # hh.setStretchLastSection(True)
        #
        #selection_model.selectionChanged.connect(self.handle_selected_cells)


        # set column width to fit contents
        self.resizeColumnsToContents()

        #delegate = PlateReaderTableDelegate()
        #elf.setItemDelegate(delegate)
        #self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        #self.selectionModel().selectionChanged.connect(self.selection_changed)

    def set_current_line(self, line):
        self.current_line = line


    # def mouseReleaseEvent(self, event):
    #     for index  in self.selectionModel().selectedIndexes():
    #         self.selectionModel().reset()
    #     self.setState(QtWidgets.QAbstractItemView.NoState)














class PlateReaderTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, headerdata, parent=None, *args):
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain[0]
        self.time = datain[1]
        self.graph_data = datain[2]
        self.current_line = ""
        self.setDataCounter = 0
        self.set_cells = list()

        self.headerdata = headerdata

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        return len(self.arraydata[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.arraydata[index.row()][index.column()]

    def get_graph_data(self, index):
        if self.arraydata[index.row()][index.column()] == 'B' or self.arraydata[index.row()][index.column()] == 'x':
            return None
        else:
            return self.graph_data[index.row()][index.column()]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        self.setDataCounter +=1
        if index.isValid():
            if self.arraydata[index.row()][index.column()] == 'B' or self.arraydata[index.row()][index.column()] == 'x':
                pass
            else:
                self.arraydata[index.row()][index.column()] = value
                self.dataChanged.emit(index,index,[])

        return True

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headerdata[0][col]
        elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole and col < len(self.headerdata[1]):
            return self.headerdata[1][col]

    def flags(self, index):
        return super(PlateReaderTableModel, self).flags(index) | QtCore.Qt.ItemIsUserCheckable

class PlateReaderTableDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent = None):
        super(PlateReaderTableDelegate, self).__init__(parent)

    def paint(self, painter, option, index):

        painter.save()

        if option.state & QtWidgets.QStyle.State_Selected:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.blue))
            painter.setPen(QtGui.QPen(QtCore.Qt.black))
            value = index.data(QtCore.Qt.DisplayRole)

            text = str(value)

            painter.drawRect(option.rect)
            #painter.drawText(option.rect, QtCore.Qt.AlignLeft, text)



        else:
            painter.setBrush(QtGui.QBrush(QtCore.Qt.white))
            painter.setPen(QtGui.QPen(QtCore.Qt.black))
            value = index.data(QtCore.Qt.DisplayRole)

            text = str(value)

            #painter.drawRect(option.rect)
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, text)

        painter.restore()


    # def sort(self, Ncol, order):
    #     """Sort table by given column number.
    #     """
    #     self.emit(SIGNAL("layoutAboutToBeChanged()"))
    #     self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
    #     if order == Qt.DescendingOrder:
    #         self.arraydata.reverse()
    #     self.emit(SIGNAL("layoutChanged()"))


if __name__ == "__main__":
    main()