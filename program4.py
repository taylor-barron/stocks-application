import wx
import sqlite3
import wx.lib.mixins.listctrl as mixlist 
import requests
import datetime

class MyListCtrl(wx.ListCtrl, mixlist.TextEditMixin, mixlist.ListCtrlAutoWidthMixin): 
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, style=0): 
        wx.ListCtrl.__init__(self, parent, ID, pos, size=(900, 250), style=wx.LC_REPORT)  # ListCtrl constructor 
        mixlist.TextEditMixin.__init__(self)  # call this constructor too 
        mixlist.ListCtrlAutoWidthMixin.__init__(self)  # call this constructor too 

        #insert columns
        self.InsertColumn(0, 'Company', width=150)
        self.InsertColumn(1, 'Symbol', width=150)
        self.InsertColumn(2, 'Purchase Price', width=150)
        self.InsertColumn(3, 'Current Price', width=150)
        self.InsertColumn(4, 'Shares', width=150)
        self.InsertColumn(5, 'Gain/Loss', width=150)
 
        #self.populate_list()   # read table data, populate list control 
 
class MyFrame(wx.Frame): 
 
    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, 
                         size=(940, 450), style=wx.DEFAULT_FRAME_STYLE, name="MyFrame"): 
        super(MyFrame, self).__init__(parent, id, title, pos, size, style, name) 
 
        panel = wx.Panel(self, wx.ID_ANY) 

        self.list = MyListCtrl(panel, -1, style=wx.LC_REPORT, pos=(20, 80), size=(500, 260))

        self.gainsOrLosses = wx.StaticText(panel, label='Total', pos=(450, 35))
        self.date = wx.StaticText(panel, label="Today's Date", pos=(450, 15))

        self.cancelBtn = wx.Button(panel, -1, 'Close', size=(-1, 30), pos=(380, 350)) 
        self.cancelBtn.Bind(wx.EVT_BUTTON, self.OnCancel) 
 
        self.Centre() 
        self.Show(True) 

        self.displayBtn = wx.Button(panel, -1, 'Display', size=(-1, 30), pos=(480, 350))
        self.displayBtn.Bind(wx.EVT_BUTTON, self.displayAllData)

    def displayAllData(self, event):
        self.list.DeleteAllItems() # clear all rows in list 
 
        try: 
            con = sqlite3.connect('tech_stocks.db') 
            cur = con.cursor() 
 
            cur.execute("SELECT * FROM dow_stocks")
            results = cur.fetchall() 

            total = 0
 
            for row in results:
                # eliminate unused table data from tuple
                row = row[1:]
                row = row[:1] + row[2:]
                # use api to retrieve data for current price
                apiString = 'https://finnhub.io/api/v1/quote?symbol=' + row[1] + '&token=c8pq6qqad3icps1ju220'
                r = requests.get(apiString)
                stockAPI = r.json()
                currentPrice = stockAPI['c']
                # calculations for gains/losses
                purchaseTotal = row[3] * row[2]
                currentTotal = currentPrice * row[2]
                gainLoss = currentTotal - purchaseTotal
                total += gainLoss
                # currency formatting for table
                currentPriceFormatted = "${:,.2f}".format(float(stockAPI['c']))
                purchaseTotalFormatted = "${:,.2f}".format(row[3])
                if gainLoss < 0:
                    gainLossFormatted = "-${:,.2f}".format(abs(gainLoss))
                else:
                    gainLossFormatted = "${:,.2f}".format(gainLoss)
                rowList = (row[0], row[1], purchaseTotalFormatted, currentPriceFormatted, row[2], gainLossFormatted)

                self.list.Append(rowList) 
 
            cur.close() 
            con.close() 

            # display total
            if total < 0:
                self.gainsOrLosses.SetLabel("Net gain/loss: -${:,.2f}".format(abs(total)))
            else:
                self.gainsOrLosses.SetLabel("Net gain/loss: ${:,.2f}".format(total))

            # display date
            dateNTime = datetime.datetime.now()
            self.date.SetLabel(dateNTime.strftime("%A %B %d, %Y : %H:%M"))
 
        except sqlite3.Error as error: 
            dlg = wx.MessageDialog(self, str(error), 'Error occured') 
            dlg.ShowModal()
     
    def OnCancel(self, event): 
        self.Close() 

if __name__ == '__main__': 
    app = wx.App() 
    MyFrame(None, -1, 'Stocks Portfolio') 
    app.MainLoop() 