import os, logging, wx, time, datetime, Queue, printer, textwrap
from qrcode import *
from wx import xrc
from threading import *
from Datasource import Datasource
from BillAcceptor import BillAcceptor

q = Queue.Queue()
GET_EXCHANGE_RATE_ID = wx.NewId()
GET_INSERTED_AMOUNT_ID = wx.NewId()
class BitcoinATM(wx.App):

	def OnInit(self):
		self.res = xrc.XmlResource('gui.xrc')
		self.init_frame()
		return True
	def init_frame(self):
		self.frame = self.res.LoadFrame(None, 'mainFrame')
		self.scanPanel = xrc.XRCCTRL(self.frame, 'scanPanel')
		self.insertPanel = xrc.XRCCTRL(self.frame, 'insertPanel')
		self.insertPanel.Hide()
		self.boughtPanel = xrc.XRCCTRL(self.frame, 'boughtPanel')
		self.boughtPanel.Hide()
		self.price_label = xrc.XRCCTRL(self.scanPanel, 'price_label')
		self.identity_textbox = xrc.XRCCTRL(self.scanPanel, 'identity')
		self.identity_textbox.SetFocus()
		self.amount_inserted_label = xrc.XRCCTRL(self.insertPanel, 'amount_inserted_label')
		self.qr_code_image = xrc.XRCCTRL(self.boughtPanel, 'qr_code_image')

		self.frame.Bind(wx.EVT_BUTTON, self.OnScanned, id=xrc.XRCID('next') )
		self.frame.Bind(wx.EVT_BUTTON, self.OnBuy, id=xrc.XRCID('buy') )
		self.frame.Bind(wx.EVT_BUTTON, self.OnAgain, id=xrc.XRCID('again') )
		self.Connect(-1, -1, GET_EXCHANGE_RATE_ID, self.GetExchangeRate)
		self.Connect(-1, -1, GET_INSERTED_AMOUNT_ID, self.GetInsertedAmount)
		DataWorker(self)
		self.frame.Show()
	def OnScanned(self, event):
		self.scanPanel.Hide()
		self.insertPanel.Show()
		# send authorization request to bitcoin api
		#
		#
		self.acceptor = Acceptor(self)
	def OnBuy(self, event):
		self.insertPanel.Hide()
		self.boughtPanel.Show()
		self.acceptor.abort()
		# send request to bitcoin api and get bitcoin private key
		#
		#
		self.CreateQR("E9873D79C6D87DC0FB6A5778633389F4453213303DA61F20BD67FC233AA33262")
		self.amount_inserted_label.SetLabel("")
	def OnAgain(self, event):
		self.boughtPanel.Hide()
		self.scanPanel.Show()
	def CreateQR(self, string):
		qr = QRCode(version=1, box_size=3, border=1)
		qr.add_data(string)
		qr.make(fit=True)

		im = qr.make_image()
		qrfile = os.path.join("tmp", str(time.time() ) + ".png")
		image = open(qrfile, 'wb')
		im.save(image, "PNG")
		self.qr_code_image.SetBitmap(wx.BitmapFromImage(wx.Image(qrfile, wx.BITMAP_TYPE_ANY) ) )
	def GetExchangeRate(self, event):
		self.price_label.SetLabel(str(event.data['exchange_rate']) )
	def GetInsertedAmount(self, event):
		self.amount_inserted_label.SetLabel(str(event.data) )

class ResultEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data."""
	def __init__(self, event_id, data):
		"""Init Result Event."""
		wx.PyEvent.__init__(self)
		self.SetEventType(event_id)
		self.data = data
class DataWorker(Thread):
	def __init__(self, main_window):
		Thread.__init__(self)
		self._main_window = main_window
		self.d = Datasource()
		self.start()
	def run(self):
		while True:
			result = self.d.test()
			wx.PostEvent(self._main_window, ResultEvent(GET_EXCHANGE_RATE_ID, result) )
			time.sleep(1)
class Acceptor(Thread):
	def __init__(self, main_window):
		Thread.__init__(self)
		self._abort = False
		self.b = BillAcceptor()
		self.start()
		self._main_window = main_window
	def run(self):
		result = []
		stacking = None
		iterator = 0
		start_time = time.time()
		#get inserted amount
		while True:
			status = self.b.run(iterator, stacking)
			if status is not None:
				if(status['status'] == 'IDLE' and time.time() - start_time > 60): #reset GUI after 60 seconds
					wx.PostEvent(self._main_window, ResultEvent({
						'error_code' : 'l1',
						'error_txt' : 'Timeout'
					}) )
					return
				if status['status'] == 'ESCROWED':
					stacking = True
				iterator += 1
				time.sleep(1)
				wx.PostEvent(self._main_window, ResultEvent(GET_INSERTED_AMOUNT_ID, status['total']) )
			if self._abort:
				return
	def abort(self):
		self._abort = True
	#duplicate method, Main class has one as well
	def AsciiToUnicode(self, ascii_text):
		decoded = ascii_text.decode('utf-8')
		unicode(decoded)
		return decoded
if __name__ == '__main__':
	app = BitcoinATM(False)
	app.MainLoop()
