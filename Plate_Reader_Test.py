import unittest
import sys
from Plate_Reader_Graph import Plate_Reader as pr
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtTest
import sip
from unittest.mock import patch


app = QtWidgets.QApplication(sys.argv)

# class TestPlateTable(unittest.TestCase):
#
#     def setUp(self):
#         data = [['A1', 'B1', 'C1'],
#                 ['A2', 'B2', 'C2'],
#                 ['A3', 'B3', 'C3'],
#                 ['A4', 'B4', 'C4']]
#         plate_data = pr.PlateDataModel(data)
#         self.plate_table = pr.PlateReaderTable(plate_data)
#
#     def test_plate_table_class(self):
#         self.assertIsInstance(self.plate_table, pr.PlateReaderTable)



class TestDataFactory(unittest.TestCase):

    def test_white_space_generation(self):
        dataf = pr.PlateReaderData()
        self.assertEqual(12, len(dataf.get_table_data()[0]))
        self.assertEqual(7, len(dataf.get_table_data()))



    def test_remove_non_selected_data(self):
        dataf = pr.PlateReaderData()
        model = pr.PlateReaderTableModel(dataf.get_table_data(),[])
        set_indexes = list()
        new_indexes = list()
        #Create list of QModelIndexes for testing
        print(len(range(0,3)))
        for x in range(0,3):
            set_indexes.append(model.index(0,x))
            new_indexes.append(model.index(x,0))

        #Set initial values in model
        for index in set_indexes:
            model.setData(index, '1')

        deselected_cells = [x for x in set_indexes if x not in set(new_indexes)]
        self.assertEqual(2, len(deselected_cells))

        for index in deselected_cells:
            model.setData(index, "")
            self.assertEqual("", model.data(index, QtCore.Qt.DisplayRole))

        for index in new_indexes:
            model.setData(index, '1')
            self.assertEqual('1', model.data(index, QtCore.Qt.DisplayRole))




# class TestPlateDataModel(unittest.TestCase):
#
#     def test_plate_data_model(self):
#
#         data = [['A1', 'B1', 'C1'],
#                 ['A2', 'B2', 'C2'],
#                 ['A3', 'B3', 'C3'],
#                 ['A4', 'B4', 'C4']]
#
#
#         self.plate_data = pr.PlateDataModel(data)
#         index = self.plate_data.index(2,2)
#         self.assertIsInstance(self.plate_data, pr.PlateDataModel)
#         self.assertEqual(4, self.plate_data.rowCount())
#         self.assertEqual(3, self.plate_data.columnCount())
#         self.assertEqual('C4', self.plate_data.data(index,None))









