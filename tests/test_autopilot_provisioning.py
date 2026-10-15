import tempfile
import unittest
from pathlib import Path
from src.autopilot.provisioning import NumberProvisioning

NUMBER="+15551234567"
ACCOUNT="AC"+"a"*32
class TestProvisioning(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.registry=NumberProvisioning(str(Path(tmp.name)/"registry.sqlite"))

    def test_provision_and_verify(self):
        self.assertTrue(self.registry.provision(phone_number=NUMBER,tenant_id="shop-a",
                                               provider_account_sid=ACCOUNT).accepted)
        self.assertTrue(self.registry.verify(phone_number=NUMBER,tenant_id="shop-a",
                                             provider_account_sid=ACCOUNT))

    def test_wrong_tenant_rejected(self):
        self.registry.provision(phone_number=NUMBER,tenant_id="shop-a",provider_account_sid=ACCOUNT)
        self.assertFalse(self.registry.verify(phone_number=NUMBER,tenant_id="shop-b",
                                              provider_account_sid=ACCOUNT))

    def test_wrong_provider_account_rejected(self):
        self.registry.provision(phone_number=NUMBER,tenant_id="shop-a",provider_account_sid=ACCOUNT)
        self.assertFalse(self.registry.verify(phone_number=NUMBER,tenant_id="shop-a",
                                              provider_account_sid="AC"+"b"*32))

    def test_conflicting_ownership_rejected(self):
        self.registry.provision(phone_number=NUMBER,tenant_id="shop-a",provider_account_sid=ACCOUNT)
        self.assertEqual(self.registry.provision(phone_number=NUMBER,tenant_id="shop-b",
                         provider_account_sid=ACCOUNT).reason,"number_owned_by_other_account")

    def test_disable_blocks(self):
        self.registry.provision(phone_number=NUMBER,tenant_id="shop-a",provider_account_sid=ACCOUNT)
        self.registry.disable(NUMBER)
        self.assertFalse(self.registry.verify(phone_number=NUMBER,tenant_id="shop-a",
                                              provider_account_sid=ACCOUNT))

    def test_invalid_provisioning(self):
        self.assertFalse(self.registry.provision(phone_number="bad",tenant_id="shop-a",
                                                  provider_account_sid=ACCOUNT).accepted)

if __name__=="__main__":
    unittest.main()
