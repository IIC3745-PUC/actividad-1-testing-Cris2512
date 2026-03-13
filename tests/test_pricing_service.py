import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):

	def setUp(self):
		self.service = PricingService()
		self.subtotal = 10000

	def testSubtotalValid(self):
		lista = [CartItem("QWERT", 10, 2), CartItem("ASDF", 5, 1)]
		subtotal = self.service.subtotal_cents(lista)
		self.assertEqual(subtotal, 25)
	
	def testSubtotalInvalidQuantity(self):
		lista = [CartItem("QWERT", 10, -2), CartItem("ASDF", 5, 1)]
		self.assertRaises(PricingError, self.service.subtotal_cents, lista)
	
	def testSubtotalInvalidUnitPrice(self):
		lista = [CartItem("QWERT", 10, 2), CartItem("ASDF", -5, 1)]
		self.assertRaises(PricingError, self.service.subtotal_cents, lista)
	
	def testCouponNone(self):
		subtotalDescontado = self.service.apply_coupon(self.subtotal, None)
		self.assertEqual(self.subtotal, subtotalDescontado)
	
	def testCouponWhiteSpace(self):
		subtotalDescontado = self.service.apply_coupon(self.subtotal, "   ")
		self.assertEqual(self.subtotal, subtotalDescontado)
	
	def testCoupon10(self):
		subtotalDescontado = self.service.apply_coupon(self.subtotal, "SAVE10")
		self.assertEqual(self.subtotal * 0.9, subtotalDescontado)
	
	def testCoupon2000(self):
		subtotalDescontado = self.service.apply_coupon(self.subtotal, "CLP2000")
		self.assertEqual(self.subtotal - 2000, subtotalDescontado)
	
	def testCouponInvalid(self):
		self.assertRaises(PricingError, self.service.apply_coupon, self.subtotal, "COUPON")
	
	def testTaxCentCL(self):
		tax = self.service.tax_cents(self.subtotal, "CL")
		self.assertEqual(self.subtotal * 0.19, tax)
	
	def testTaxCentEU(self):
		tax = self.service.tax_cents(self.subtotal, "EU")
		self.assertEqual(self.subtotal * 0.21, tax)

	def testTaxCentUS(self):
		tax = self.service.tax_cents(self.subtotal, "US")
		self.assertEqual(self.subtotal * 0, tax)
		
	def testTaxUnsupported(self):
		self.assertRaises(PricingError, self.service.tax_cents, self.subtotal, "ES")
	
	def testShippingCentCLOver20000(self):
		value = self.service.shipping_cents(25000, "CL")
		self.assertEqual(0, value)

	def testShippingCentCLUnder20000(self):
		value = self.service.shipping_cents(self.subtotal, "CL")
		self.assertEqual(2500, value)
	
	def testShippingCentUS(self):
		value = self.service.shipping_cents(self.subtotal, "US")
		self.assertEqual(5000, value)
	
	def testShippingCentEU(self):
		value = self.service.shipping_cents(self.subtotal, "EU")
		self.assertEqual(5000, value)
	
	def testShippingCentUnsupportedCountry(self):
		self.assertRaises(PricingError, self.service.shipping_cents, self.subtotal, "ES")
	
	def testTotalValue(self):
		lista = [CartItem("QWERT", 5000, 2)]
		coupon = None
		country = "CL"
		total = self.service.total_cents(lista, coupon, country)
		self.assertEqual(10000 * 1.19 + 2500, total)