from escpos.printer import Usb

""" Seiko Epson Corp. Receipt Printer (EPSON TM-T88III) """
p = Usb(0x04b8, 0x0e32, 0, profile='TM-T20II')
p.text("Hello World\n")
p.image("../clove.jpg")
p.barcode('4006381333931', 'EAN13', 64, 2, '', '')
p.cut()
