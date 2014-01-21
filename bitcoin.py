import os, logging, wx, time, datetime, Queue, printer, textwrap
from threading import *
from Datasource import Datasource

q = Queue.Queue()
EVT_RESULT_ID = wx.NewId()
ID_PRICE = wx.NewId()
ID_TIMESTAMP = wx.NewId()
ID_OK = wx.NewId()
class Main(wx.Frame):
	def __init__(self, parent, title):
		super(Main, self).__init__(parent, title=title, size=(640, 350) )
		self.panel = wx.Panel(self)
		self.Connect(-1, -1, EVT_RESULT_ID, self.OnResult)
		self.vbox_input = wx.BoxSizer(wx.VERTICAL)
		currentPrice = "NA"
		data_worker = DataWorker(self, 'get_price')
		self.vbox_input.Add(wx.StaticText(self.panel, ID_PRICE, "Current Price: " + str(currentPrice) ), flag=wx.EXPAND )
		self.vbox_input.Add(wx.Button(self.panel, id=ID_OK, label='Buy'), flag=wx.EXPAND )
		self.panel.SetSizer(self.vbox_input)
		self.Show()
	def OnResult(self, event):
		for sizerItem in self.vbox_input.GetChildren():
			widget = sizerItem.GetWindow()
			if(widget.GetId() == ID_PRICE):
				widget.SetLabel("Current Price: " + str(event.data['price']) )

class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RESULT_ID)
		self.data = data
class DataWorker(Thread):
	def __init__(self, main_window, action):
		Thread.__init__(self)
		self.action = action
		self._main_window = main_window
		self.d = Datasource()
		self.start()
	def run(self):
		while True:
			result = self.d.get_price()
			wx.PostEvent(self._main_window, ResultEvent(result) )
			time.sleep(1)
def main():
	app = wx.App()
	Main(None, "Square Potato")
	app.MainLoop()

if __name__ == '__main__':
	main()

