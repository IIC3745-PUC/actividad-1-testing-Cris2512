import unittest
from unittest.mock import Mock
from unittest.mock import patch

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	
	def setUp(self):
		payments = Mock()
		email = Mock()
		fraud = Mock()
		repo = Mock()
		pricing = PricingService()
		checkout = CheckoutService(payments, email, fraud, repo, pricing)
		self.checkout = checkout

	def testCreateChargeResult(self):
		charge = ChargeResult(True)
		self.assertTrue(charge.ok)
		self.assertEqual(charge.charge_id, None)
		self.assertEqual(charge.reason, None)
		self.charge = charge	
	
	def testInvalidUser(self):
		lista = [CartItem("QWERT", 10, 2), CartItem("ASDF", 5, 1)]
		check = self.checkout.checkout("   ", lista, "asdf", "CL", None)
		self.assertEqual("INVALID_USER", check)
	
	def testInvalidCartQuantity(self):
		lista = [CartItem("QWERT", 10, -2), CartItem("ASDF", 5, 1)]
		check = self.checkout.checkout("abcd", lista, "asdf", "CL", None)
		self.assertEqual(check, "INVALID_CART:qty must be > 0")
		
	def testInvalidCartUnitPrice(self):
		lista = [CartItem("QWERT", -10, 2), CartItem("ASDF", 5, 1)]
		check = self.checkout.checkout("abcd", lista, "asdf", "CL", None)
		self.assertEqual(check, "INVALID_CART:unit_price_cents must be >= 0")
	
	def testRejectedFraud(self):
		self.checkout.fraud.score.return_value = 90
		lista = [CartItem("QWERT", 10, 2), CartItem("ASDF", 5, 1)]
		check = self.checkout.checkout("abcd", lista, "asdf", "CL", None)
		self.assertEqual("REJECTED_FRAUD", check)
	
	def testPaymentFailed(self):
		result = Mock()
		result.ok = False
		result.reason = "No Authorized"
		self.checkout.payments.charge.return_value = result
		self.checkout.fraud.score.return_value = 50
		lista = [CartItem("QWERT", 10, 2), CartItem("ASDF", 5, 1)]
		check = self.checkout.checkout("abcd", lista, "asdf", "CL", None)
		self.assertEqual("PAYMENT_FAILED:No Authorized", check)

	@patch("src.checkout.uuid.uuid4")
	def testOrderOK(self, mock_uuid):
		mock_uuid.return_value = "abcdefg"
		result = Mock()
		result.ok = True
		self.checkout.payments.charge.return_value = result
		self.checkout.fraud.score.return_value = 50
		lista = [CartItem("QWERT", 10, 2), CartItem("ASDF", 5, 1)]
		check = self.checkout.checkout("abcd", lista, "asdf", "CL", None)
		self.assertEqual("OK:abcdefg", check)
