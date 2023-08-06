# pyhubtel-sms

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black) [![license](https://img.shields.io/badge/license-apache%202.0-brightgreen.svg)](http://www.apache.org/licenses/LICENSE-2.0)



This package provides a convenient and easy way to use / integrate [Hubtel](https://hubtel.com)'s SMS APIs in your python project.

**NOTE:** This project is a beta release and as such might be subject to minor changes in the future. 



## Installation

Install and update using [pip](https://pip.pypa.io/en/stable/quickstart/).

```sh
pip install -U pyhubtel-sms
🎉
```



## A Simple Example

```python
>>> # send an SMS to a single recipient
>>> from pyhubtel_sms import SMS
>>> sms = SMS(client_id='iwwofuxx', client_secret='icctaeik')
>>> sms.send_message(sender='PyHubtel', recipient='0502345678', content='Hello world', registered_delivery=True)
{'MessageId': 'f2665231-522f-32b6-accf-6ac8426bfd5c', 'Rate': 1, 'NetworkId': '62002', 'Status': 0}
```



## Usage

Below are usage examples for the implemented [send message][1] and [batch sms][2] APIs.

#### Send a message to a single recipient

```python
>>> from pyhubtel_sms import SMS, Message
>>> sms = SMS(client_id='iwwofuxx', client_secret='icctaeik')
>>> message = Message(
...     sender='PyHubtel',
...     content='Apples',
...     recipient='0502345678',
...     registered_delivery=True,
... )
>>> sms.send(message)
{'Status': 0, 'NetworkId': '62002', 'MessageId': '3f20fe72-e0fd-437b-b63d-dbf2b0af9c8b', 'Rate': 1}
```



#### Send the same message to different recipients

```python
>>> from pyhubtel_sms import SMS, Message
>>> sms = SMS(client_id='iwwofuxx', client_secret='icctaeik')
>>> bulk_message_one = Message(
...     sender='PyHubtel',
...     content='Oranges',
...     recipients=['0202345678', '0502345678'],
...     campaign_name='PyHubtel SMS Campaign',
... )
>>> sms.send(bulk_message_one)
{'Status': 'Scheduled', 'Name': 'PyHubtel SMS Campaign', 'SenderId': 'PyHubtel', 'TotalCount': 2, 'Time': '2018-04-06 04:16', 'Id': 664544, 'Stats': {'Pending': 2}}
```



#### Send personalized messages to recipients

```python
>>> from pyhubtel_sms import SMS, Message, Messages
>>> sms = SMS(client_id='iwwofuxx', client_secret='icctaeik')
>>> message_one = Message(
...     content='Apple Pie',
...     recipient='0202345678',
... )
>>> message_two = Message(
...     content='Orange Tart',
...     recipient='0572345678',
... )
>>> bulk_message_two = Messages(
...     sender='PyHubtel',
...     campaign_name='PyHubtel SMS Campaign',
...     batch=[message_one, message_two],
...     time='12:46 pm'
... )
>>> sms.send(bulk_message_two)
{'Stats': {'Pending': 2}, 'Status': 'Scheduled', 'Time': '2018-04-07 12:46', 'SenderId': 'PyHubtel', 'TotalCount': 2, 'Name': 'PyHubtel SMS Campaign','Id': 664817}
```



## Contributing

All contributions are welcome - from typo fixes to complete refactors and new features. If you happen to encounter a bug or would like to suggest an improvement, please feel free to open an issue or submit a pull request.



## License

This project is released under the [Apache License, Version 2.0].

[1]: https://developers.hubtel.com/documentations/sendmessage
[2]: https://developers.hubtel.com/documentations/batch-sms-api
[Apache License, Version 2.0]: http://www.apache.org/licenses/LICENSE-2.0
