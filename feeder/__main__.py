import wx
import wx.html2
import pickle
import textwrap
from wx.lib import scrolledpanel
from . import feedparse
import re
from os import path


class FeederWin(wx.Frame):
    def __init__(self, ChannelID=0):
        super().__init__(None, title='News Reader', size=(1000, 700), pos=(30, 100))
        self.channeldata = {}
        self.channelid = ChannelID
        panel = wx.Panel(self)

        self.leftpanel = LeftPanel(panel, size=(270, 650))
        self.webview = wx.html2.WebView.New(panel)
        toolbar = wx.Panel(panel, size=(270, 40))

        rbmp = wx.Bitmap(wx.Image(here + 'img/refresh.png', type=wx.BITMAP_TYPE_PNG).Scale(16, 16))
        cbmp = wx.Bitmap(wx.Image(here + 'img/config.png', type=wx.BITMAP_TYPE_PNG).Scale(16, 16))
        config = wx.BitmapButton(toolbar, bitmap=cbmp, style=wx.BORDER_NONE, size=(25, 25), pos=(5, 20))
        refresh = wx.BitmapButton(toolbar, bitmap=rbmp, style=wx.BORDER_NONE, size=(25, 25), pos=(40, 20))
        refresh.Bind(wx.EVT_BUTTON, self.getChannel)
        config.Bind(wx.EVT_BUTTON, self.toConfig)

        self.combobox = wx.ComboBox(toolbar, size=(150, 25), pos=(100, 20))
        self.combobox.Bind(wx.EVT_COMBOBOX, self.changeChannel)

        hbox = wx.BoxSizer()
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.leftpanel, proportion=1, flag=wx.EXPAND)
        vbox.Add(toolbar, proportion=0)
        hbox.Add(vbox, proportion=0, flag=wx.ALL, border=5)
        hbox.Add(self.webview, proportion=1, flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        panel.SetSizer(hbox)

        self.getChannel()

    def setChannelId(self, newid):
        self.channelid = newid

    def changeChannel(self, event):
        key = event.GetEventObject().GetSelection()
        self.setChannelId(key)
        self.getChannel()

    def getChannel(self, event=None):
        try:
            channelnames = []
            for item in Channels:
                channelnames.append(item[0])
            self.combobox.SetItems(channelnames)
            self.combobox.SetSelection(self.channelid)
            pname = feedparse.myparser(self.channelid)
            with open(here + 'pickles/' + pname[0] + '.pickle', 'rb') as f:
                self.channeldata = pickle.load(f)
            titles = []
            for item in self.channeldata['items']:
                titles.append(item['title'])
            self.leftpanel.DestroyChildren()
            self.leftpanel.addRows(titles)
            self.webview.SetPage(feedparse.myrender(self.channeldata['items'][0]), '')
            if pname[1] < 0:
                wx.MessageBox('Off-line news', caption='Tip')
        except Exception as e:
            print(e)
            wx.MessageBox('Please make sure Internet connected and rss valid.', caption='Tip')

    def toConfig(self, event):
        configwin = ConfigWin(self, title='Config', size=(400, 300), pos=(100, 50))
        configwin.Show()


class LeftPanel(scrolledpanel.ScrolledPanel):
    def __init__(self, *args1, **args2):
        super().__init__(*args1, **args2)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)

    def addRows(self, items):
        for index, item in enumerate(items):
            wraptitle = textwrap.fill(item, width=18)
            stext = wx.StaticText(self, index, wraptitle)
            self.vbox.Add(stext, 0, wx.ALIGN_LEFT | wx.ALL, 5)
            self.vbox.Add(wx.StaticLine(self, -1, size=(300, -1)), 0, wx.ALL, 5)
            stext.Bind(wx.EVT_LEFT_UP, self.getArticle)
        self.SetupScrolling(scroll_x=False)

    def getArticle(self, event):
        partId = event.GetEventObject().GetId()
        win.webview.SetPage(feedparse.myrender(win.channeldata['items'][partId]), '')
        # 这里用到了外部对象 win，需要修改


class ConfigWin(wx.Frame):
    def __init__(self, *args1, **args2):
        super().__init__(*args1, **args2)
        font = wx.Font()
        font.SetPointSize(14)
        self.SetFont(font)
        panel = wx.Panel(self)
        self.listctrl = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.listctrl.AppendColumn('Name', format=wx.LIST_FORMAT_LEFT, width=100)
        self.listctrl.AppendColumn('URL', format=wx.LIST_FORMAT_CENTRE, width=300)
        self.getData()
        toolbar = wx.Panel(panel, size=(400, 40))
        addbmp = wx.Bitmap(wx.Image(here + 'img/jiahao.png', type=wx.BITMAP_TYPE_PNG).Scale(16, 16))
        removebmp = wx.Bitmap(wx.Image(here + 'img/jianhao.png', type=wx.BITMAP_TYPE_PNG).Scale(16, 16))
        editbmp = wx.Bitmap(wx.Image(here + 'img/bianji.png', type=wx.BITMAP_TYPE_PNG).Scale(16, 16))
        add = wx.BitmapButton(toolbar, bitmap=addbmp, size=(25, 25), pos=(5, 10), id=1)
        remove = wx.BitmapButton(toolbar, bitmap=removebmp, size=(25, 25), pos=(35, 10), id=2)
        edit = wx.BitmapButton(toolbar, bitmap=editbmp, size=(25, 25), pos=(65, 10), id=3)
        add.Bind(wx.EVT_BUTTON, self.eidtAndadd)
        remove.Bind(wx.EVT_BUTTON, self.removeChannel)
        edit.Bind(wx.EVT_BUTTON, self.eidtAndadd)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.listctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(toolbar, proportion=0, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        panel.SetSizer(vbox)

    def getData(self):
        self.listctrl.DeleteAllItems()
        self.channels = Channels
        for eachchannel in self.channels:
            self.listctrl.Append(eachchannel)

    def removeChannel(self, event):
        channelid = self.listctrl.GetFirstSelected()
        if channelid >= 0:
            self.channels.pop(channelid)
            with open(here + 'channels.pickle', 'wb') as f:
                pickle.dump(self.channels, f)
            self.getData()
            win.setChannelId(0)
            win.getChannel()

    def eidtAndadd(self, event):
        ev = event.GetEventObject().GetId()
        if ev == 3:
            channelid = self.listctrl.GetFirstSelected()
            if channelid >= 0:
                dialog = ChannelEdit(self, wintitle='Modify', channelid=channelid)
            else:
                wx.MessageBox('Choose a rss', caption='Tip')
                return
        elif ev == 1:
            dialog = ChannelEdit(self, wintitle='Add')
        dialog.ShowModal()


class ChannelEdit(wx.Dialog):
    def __init__(self, parent, wintitle, channelid=-1):
        super().__init__(parent, title=wintitle, size=(300, 150), pos=(200, 100))
        self.channels = Channels
        panel = wx.Panel(self)
        wx.StaticText(panel, label="Name", pos=(15, 20))
        wx.StaticText(panel, label="URL", pos=(15, 55))

        if channelid >= 0:
            self.name = wx.TextCtrl(panel, value=self.channels[channelid][0], pos=(55, 20), size=(230, 20))
            self.link = wx.TextCtrl(panel, value=self.channels[channelid][1], pos=(55, 55), size=(230, 20))
        else:
            self.name = wx.TextCtrl(panel, value='', pos=(55, 20), size=(230, 20))
            self.link = wx.TextCtrl(panel, value='', pos=(55, 55), size=(230, 20))

        okbtn = wx.Button(panel, label="OK", pos=(70, 90), size=(50, 20), id=channelid)
        # 这里用了id来传递参数
        cancelbtn = wx.Button(panel, label="Cancel", pos=(150, 90), size=(80, 20))
        okbtn.Bind(wx.EVT_BUTTON, self.okBehave)
        cancelbtn.Bind(wx.EVT_BUTTON, self.cancelBehave)

    def okBehave(self, event):
        okid = event.GetEventObject().GetId()
        dname = self.name.GetValue().strip()
        dlink = self.link.GetValue().strip()
        if dname and dlink and re.match(r'http[s]?://[\./\-a-zA-Z_0-9]+$', dlink):
            if okid >= 0:
                    self.channels[okid][0] = dname
                    self.channels[okid][1] = dlink
            else:
                self.channels.append([dname, dlink])
            with open(here + 'channels.pickle', 'wb') as f:
                pickle.dump(self.channels, f)
            self.Close()
            self.GetParent().getData()
            win.setChannelId(0)
            win.getChannel()
        else:
            wx.MessageBox('Please fill the field in right way.', caption='Tip')

    def cancelBehave(self, event):
        self.Close()


'''
channels = [['知乎日报', 'http://zhihurss.miantiao.me/dailyrss']]
with open(here + 'channels.pickle', 'wb') as f:
    pickle.dump(channels, f)
'''
# channels.pickle 作为前提必须存在
here = path.dirname(__file__) + path.sep
with open(here + 'channels.pickle', 'rb') as f:
    Channels = pickle.load(f)
app = wx.App()
win = FeederWin()
win.Show()
app.MainLoop()
