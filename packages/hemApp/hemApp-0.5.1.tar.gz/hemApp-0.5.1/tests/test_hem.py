import unittest
import requests_mock
import datetime
import hemApp
class Basics(unittest.TestCase):
        def test_check_init(self):
            test = {'path':'/', 'secure':True, 'verify':True}
            check = hemApp.Check('test', test)
            assert check.url == 'https://{}/'
            assert check.verify == True

        def test_check_invoke(self):
            with requests_mock.mock() as m:
                m.get('https://1.1.1.1/', text="")
                test = {'path':'/', 'secure':True, 'verify':True}
                check = hemApp.Check('test', test)
                results = check.test_list(["1.1.1.1"])
                (response, timing) = results[0]
                assert results is not None
                assert response == 200
                assert type(timing) is datetime.timedelta

        def test_check_headers(self):
            import hemApp
            with requests_mock.mock() as m:
                m.get('https://1.1.1.1/', text="",  request_headers={"host": "example.com"})
                test = {'path':'/', 'secure':True, 'verify':True, "headers":{"host":"example.com"}}
                check = hemApp.Check('test', test)
                results = check.test_list(["1.1.1.1"])
                (response, timing) = results[0]
                assert results is not None
                assert response == 200
                assert type(timing) is datetime.timedelta
                test = {'path':'/', 'secure':True, 'verify':True, "headers":{"host":"notexample.com"}}
                check = hemApp.Check('test', test)
                try:
                    results = check.test_list(["1.1.1.1"])
                    assert results == []
                except requests_mock.exceptions.NoMockAddress as m:
                    exit(m)
                    assert "host test" is "host test"

if __name__ == '__main__':
    unittest.main()