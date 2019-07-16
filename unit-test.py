import os
from shutil import rmtree
import csv

import crawler


# change this to your geckodriver path
gecko_path = "/Applications/MAMP/htdocs/simfin-ml/geckodriver"
output_dir = "unit_tests_files"


def test_crawl_rendered_all():

    files_to_be_found = [['a.pdf', 'crawling_test/simfin.com/0cf2a7bd-6e12-4e79-ad42-6be89832951e.pdf', 'https://s3-eu-west-1.amazonaws.com/crawlingtest-simfin/a.pdf', 'https://simfin.com/crawlingtest', '614824', '2'], ['b.pdf', 'crawling_test/simfin.com/f27f0d3b-9ccb-45f1-9659-ea13a0b595a9.pdf', 'https://s3-eu-west-1.amazonaws.com/crawlingtest-simfin/b', 'https://simfin.com/crawlingtest', '153572', '2'], ['a.pdf', 'crawling_test/simfin.com/1c85ecd1-fea0-418d-b8f3-8ed06ce29ebf.pdf', 'https://simfin.com/crawlingtest/a.pdf', 'https://simfin.com/crawlingtest', '614824', '2'], ['abc.pdf', 'crawling_test/simfin.com/20c67f9c-5bfa-467c-a548-eafeba296555.pdf', 'https://simfin.com/crawlingtest/abc.pdf', 'https://simfin.com/crawlingtest', '614824', '2'], ['c.pdf', 'crawling_test/simfin.com/23f13929-7d24-4761-9104-702c210868be.pdf', 'https://simfin.com/crawlingtest/c.pdf', 'https://simfin.com/crawlingtest', '722455', '2'], ['onsub.pdf', 'crawling_test/simfin.com/fc4b2ec7-e9d7-4956-bb08-a3652f39ccba.pdf', 'https://simfin.com/crawlingtest/sub/onsub.pdf', 'https://simfin.com/crawlingtest/sub', '614824', '1'], ['d.pdf', 'crawling_test/simfin.com/7607070c-4b00-460a-baae-7715a163f690.pdf', 'https://simfin.com/crawlingtest/d.pdf', 'https://simfin.com/crawlingtest', '247435', '2'], ['8.pdf', 'crawling_test/simfin.com/2d5ea4e1-55cb-4cea-ac20-4f7f9508649c.pdf', 'https://simfin.com/crawlingtest/8.pdf', 'https://simfin.com/crawlingtest', '614824', '2'], ['9.pdf', 'crawling_test/simfin.com/3b928a7e-b0a7-40fc-8943-6e3afaf63841.pdf', 'https://simfin.com/crawlingtest/9.pdf', 'https://simfin.com/crawlingtest', '614824', '2'], ['10.pdf', 'crawling_test/simfin.com/c28c820a-17b0-40ee-a6fd-026d4001ef8c.pdf', 'https://simfin.com/crawlingtest/10.pdf', 'https://simfin.com/crawlingtest', '614824', '2'], ['11.pdf', 'crawling_test/simfin.com/b6962eb1-ecc6-4198-a368-453386fc32a3.pdf', 'https://simfin.com/crawlingtest/11.pdf', 'https://simfin.com/crawlingtest', '614824', '2']]

    if os.path.isdir(output_dir):
        rmtree(output_dir)

    crawler.crawl(url="https://simfin.com/crawlingtest",output_dir=output_dir,method="rendered-all",gecko_path=gecko_path,depth=3)

    assert os.path.isdir(output_dir)
    assert os.path.isfile(os.path.join(output_dir,"simfin.com.csv"))

    with open(os.path.join(output_dir,"simfin.com.csv"), newline='') as csvfile:

        reader = list(csv.reader(csvfile, delimiter=',', quotechar='"'))

        assert len(reader) == 12
        for a in range(1,len(reader)):
            assert reader[a][0] == files_to_be_found[a-1][0]
            assert reader[a][2] == files_to_be_found[a - 1][2]
