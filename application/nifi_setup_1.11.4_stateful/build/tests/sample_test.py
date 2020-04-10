from deploy_nifi import deploy_nifi_template


def test_answer():
    assert deploy_nifi_template('http://nifi.services.tomarv2.com:80', 'http://varun.tomarv2.com/projects/DP/repos/demonifi/raw/templates', 'template.xml',  'demoapplication') == 5