#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#
import uuid

from openstack.tests.functional import base


def auto_create_cert(conn, name):
    """auto create a certificate

    :param conn:
    :param name:
    :return:
    """
    cert = {
        "name": name,
        "certificate": ("-----BEGIN CERTIFICATE-----"
                        "\nMIIDXTCCAkWgAwIBAgIJANoPUy2NktS6MA0GCSqGSIb3D"
                        "QEBBQUAMEUxCzAJBgNV\nBAYTAkFVMRMwEQYDVQQIDApTb2"
                        "1lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX\naWRnaXR"
                        "zIFB0eSBMdGQwHhcNMTYwNjIyMDMyOTU5WhcNMTkwNjIyMD"
                        "MyOTU5WjBF\nMQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29"
                        "tZS1TdGF0ZTEhMB8GA1UECgwYSW50\nZXJuZXQgV2lkZ2l0"
                        "cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB"
                        "\nCgKCAQEArmUUhzm5sxxVr/ku4+6cKqnKgZvDl+e/6CNCAq"
                        "8YMZXTpJP64DjDPny9\n+8s9MbFabEG3HqjHSKh3b/Ew3FXr"
                        "8LFa9YuWuAi3W9ii29sZsOwmzIfQhIOIaP1Y\nNR50DDjbAG"
                        "TaxzRhV40ZKSOCkaUTvl3do5d8ttD1VlF2r0w0DfclrVcsS5"
                        "v3kw88\n9gJ3s3hNkatfQiSt4qLNMehZ8Xofx58DIAOk/f3V"
                        "usj3372PsJwKX39cHX/NpIHC\nHKE8qaGCpDqv0daH766eJ0"
                        "65dqO9DuorXPaPT/nxw4PAccb9fByLrTams0ThvSlZ\no6V3"
                        "yvHR4KN7mmvbViEmWRy+9oiJEwIDAQABo1AwTjAdBgNVHQ4E"
                        "FgQUlXhcABza\n2SdXPYpp8RkWvKblCNIwHwYDVR0jBBgwFo"
                        "AUlXhcABza2SdXPYpp8RkWvKblCNIw\nDAYDVR0TBAUwAwEB"
                        "/zANBgkqhkiG9w0BAQUFAAOCAQEAHmsFDOwbkD45PF4oYdX+"
                        "\ncCoEGNjsLfi0spJ6b1CHQMEy2tPqYZJh8nGuUtB9Zd7+rb"
                        "wm6NS38eGQVA5vbWZH\nMk+uq5un7YFwkM+fdjgCxbe/3PMk"
                        "k/ZDYPHhpc1W8e/+aZVUBB2EpfzBC6tcP/DV\nSsjq+tG+JZ"
                        "IVADMxvEqVIF94JMpuY7o6U74SnUUrAi0h9GkWmeYh/Ucb3P"
                        "LMe5sF\noZriRdAKc96KB0eUphfWZNtptOCqV6qtYqZZ/UCo"
                        "tp99xzrDkf8jGkm/iBljxb+v\n0NTg8JwfmykCj63YhTKpHf"
                        "0+N/EK5yX1KUYtlkLaf8OPlsp/1lqAL6CdnydGEd/s\nAA=="
                        "\n-----END CERTIFICATE-----"),
        "private_key": ("-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQ"
                        "EArmUUhzm5sxxVr/ku4+6cKqnKgZvDl+e/6CNCAq8YMZXTpJP"
                        "6\n4DjDPny9+8s9MbFabEG3HqjHSKh3b/Ew3FXr8LFa9YuWuA"
                        "i3W9ii29sZsOwmzIfQ\nhIOIaP1YNR50DDjbAGTaxzRhV40ZK"
                        "SOCkaUTvl3do5d8ttD1VlF2r0w0DfclrVcs\nS5v3kw889gJ3"
                        "s3hNkatfQiSt4qLNMehZ8Xofx58DIAOk/f3Vusj3372PsJwKX"
                        "39c\nHX/NpIHCHKE8qaGCpDqv0daH766eJ065dqO9DuorXPaP"
                        "T/nxw4PAccb9fByLrTam\ns0ThvSlZo6V3yvHR4KN7mmvbViE"
                        "mWRy+9oiJEwIDAQABAoIBACV47rpHuxEza24O\nevbbFI9OQI"
                        "cs8xA26dN1j/+HpAkzinB4o5V+XOWWZDQwbYu58hYE4NYjqf6"
                        "AxHk3\nOCqAA9yKH2NXhSEyLkP7/rKDF7geZg/YtwNiR/NXTJ"
                        "bNXl4p8VTaVvAq3yey188x\nJCMrd1yWSsOWD2Qw7iaIBpqQI"
                        "zdEovPE4CG6GmaIRSuqYuoCfbVTFa6YST7jmOTv\nEpG+x6yJ"
                        "ZzJ4o0vvfKbKfvPmQizjL+3nAW9g+kgXJmA1xTujiky7bzm2s"
                        "LK2Slrx\n5rY73mXMElseSlhkYzWwyRmC6M+rWALXqOhVDgIG"
                        "baBV4IOzuyH/CUt0wy3ZMIpv\nMOWMNoECgYEA1LHsepCmwjl"
                        "DF3yf/OztCr/DYqM4HjAY6FTmH+xz1Zjd5R1XOq60\nYFRkhs"
                        "/e2D6M/gSX6hMqS9sCkg25yRJk3CsPeoS9v5MoiZQA8XlQNov"
                        "cpWUI2DCm\naZRIsdovFgIqMHYh/Y4CYouee7Nz7foICzO9sv"
                        "rYrbOIVmMwDVJ8vzMCgYEA0ebg\nm0lCuOunyxaSBqOv4Q4sk"
                        "7Ix0702dIrW0tsUJyU+xuXYH1P/0m+t4/KUU2cNwsg3\njiNz"
                        "QR9QKvF8yTB5TB4Ye/9dKlu+BEOskvCpuErxc6iVJ+TZOrQDD"
                        "PNcq56qez5b\nvv9EDdgzpjkjO+hS1j3kYOuG11hrP4Pox4Pi"
                        "jqECgYEAz6RTZORKqFoWsZss5VK3\np0LGkEkfw/jYmBgqAQh"
                        "pnSD7n20hd1yPI2vAKAxPVXTbWDFLzWygYiWRQNy9fxrB\n9F"
                        "7lYYqtY5VagdVHhnYUZOvtoFoeZFA6ZeAph9elGCtM3Lq3PD2"
                        "i/mmncsQibTUn\nHSiKDWzuk8UtWIjEpHze5BkCgYEAifD9eG"
                        "+bzqTnn1qU2pIl2nQTLXj0r97v84Tu\niqF4zAT5DYMtFeGBB"
                        "I1qLJxVh7342CH2CI4ZhxmJ+L68sAcQH8rDcnGui1DBPlIv\n"
                        "Dl3kW3280bJfW1lUvPRh8NfZ9dsO1HF1n75nveVwg/OWyR7zm"
                        "WIRPPRrqAeua45H\nox5z/CECgYBqwlEBjue8oOkVVu/lKi6f"
                        "o6jr+0u25K9dp9azHYwE0KNHX0MwRALw\nWbPgcjge23sfhbe"
                        "qVvHo0JYBdRsk/OBuW73/9Sb5E+6auDoubCjC0cAIvs23MPju"
                        "\nsMvKak4mQkI19foRXBydB/DDkK26iei/l0xoygrw50v2HEr"
                        "sQ7JcHw==\n-----END RSA PRIVATE KEY-----")
    }
    return conn.load_balancer.create_certificate(**cert)


class TestCertificate(base.BaseFunctionalTest):
    NAME = "SDK-" + uuid.uuid4().hex
    lb = None
    router = None

    @classmethod
    def setUpClass(cls):
        super(TestCertificate, cls).setUpClass()
        cls.cert = auto_create_cert(cls.conn, cls.NAME)

    @classmethod
    def tearDownClass(cls):
        cls.conn.load_balancer.delete_certificate(cls.cert)
        certs = list(cls.conn.load_balancer.certificates())
        if cls.cert.id in [c.id for c in certs]:
            raise Exception("delete cert failed")

    def test_list_cert(self):
        certs = list(self.conn.load_balancer.certificates())
        self.assertIn(self.cert.id, [c.id for c in certs])

    def test_update_cert(self):
        updated = {
            "description": "certificate created by unittests"
        }
        cert = self.conn.load_balancer.update_certificate(self.cert, **updated)
        certs = list(self.conn.load_balancer.certificates())
        for _cert in certs:
            if _cert.id == cert.id:
                self.assertEqual(updated["description"], cert.description)
