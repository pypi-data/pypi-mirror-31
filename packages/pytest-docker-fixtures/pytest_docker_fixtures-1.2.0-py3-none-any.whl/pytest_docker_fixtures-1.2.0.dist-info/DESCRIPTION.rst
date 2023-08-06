Introduction
============

Provide various service pytest fixtures.


Install
-------

`pip install pytest-docker-fixtures`

Usages
------

In your conftest.py, add the following:

    pytest_plugins = ['pytest_docker_fixtures']


And to use the fixtures:

    def test_foobar(redis):
        pass


Available fixtures
------------------

PRs welcome!

- redis
- etcd
- pg(require to be installed with `pip install pytest-docker-fixtures[pg]`)
- cockroach(require to be installed with `pip install pytest-docker-fixtures[pg]`)
- es


Configuring custom images
-------------------------

You can also configure custom images to use::

    from pytest_docker_fixtures import images
    images.configure(
        'elasticsearch',
        'docker.elastic.co/elasticsearch/elasticsearch-platinum', '6.2.4')

1.2.0 (2018-05-05)
------------------

- Be able to configure custom docker images
  [vangheem]

1.1.0 (2018-04-03)
------------------

- Add Elasticsearch fixture
  [vangheem]


1.0.1 (2018-03-12)
------------------

- release


1.0.0 (2018-03-12)
------------------

- initial release


