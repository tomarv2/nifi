from deploy_nifi import deploy_nifi_template


def test_answer():
    assert deploy_nifi_template('http://nifi.services.demo.com:80', 'http://varun.demo.com/projects/DP/repos/demonifi/raw/templates', 'template.xml',  'demoapplication') == 5