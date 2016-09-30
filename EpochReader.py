
from openpyxl import load_workbook
import unittest

class TestEpochDataReader(unittest.TestCase):

    def setUp(self):
        self.data = EpochDataReader("secondPlateReader.xlsx")

    def test_worksheet(self):
        self.assertEqual(self.data.worksheet.title, 'Plate 1 - Sheet1')

    def test_getTableLayout(self):
        self.assertEqual(len(self.data.wellTableLayout), 8)
        self.assertEqual(len(self.data.wellTableLayout[0]), 12)

    def test_tableviewlayout(self):
        self.assertEqual(self.data.view_layout[0][0], " ")
        self.assertEqual(self.data.view_layout[7], [" "," "," "," "," "," "," "," "," ","B","B","B"])

    def test_blank650_results_range(self):
        self.assertEquals(self.data.results_range, 53)

    def test_time(self):
        self.assertEqual(len(self.data.time), 48)

class EpochDataReader:

    def __init__(self, filename):
        workbook = load_workbook(filename, read_only=True)
        self.worksheet = workbook['Plate 1 - Sheet1']

        self.wellTableLayout = self.worksheet['C30:N37']
        self.view_layout = list()

        self.set_tableview_values()
        self.results_range = 0
        blank_row = 0
        results_row =0

        print(blank_row)

        for row in self.worksheet.rows:

            if row[0].value == 'Blank 650':
                blank_row = row[0].row
                print(row[0].value)
            elif row[0].value == 'Results':
                results_row = row[0].row
                print(row[0].value)

        self.results_range = results_row - blank_row

    def set_tableview_values(self):

        for row in self.wellTableLayout:
            row_list = list()
            for cell in row:
                if 'SPL' in cell.value:
                    row_list.append(" ")

                elif 'BLK' in cell.value:
                    row_list.append("B")
                else:
                    row_list.append("x")
            self.view_layout.append(row_list)




if __name__ == "__main__":
    sdfds = EpochDataReader("secondPlateReader.xlsx")