=============
requests-mock
=============

.. _requests-mock_1.5.0:

1.5.0
=====

.. _requests-mock_1.5.0_Prelude:

Prelude
-------

.. releasenotes/notes/repo-move-15e956e1d54c048b.yaml @ b'33d9cc8468f89063934a58c08eb9d04e09aae895'

The primary repository is now at https://github.com/jamielennox/requests-mock


.. _requests-mock_1.5.0_New Features:

New Features
------------

.. releasenotes/notes/pytest-7e35da8c5f2cd428.yaml @ b'a455a735d7edba5d064380eb054021a11d076f57'

- Added pytest fixture for native integration into pytest projects.


.. _requests-mock_1.5.0_Other Notes:

Other Notes
-----------

.. releasenotes/notes/repo-move-15e956e1d54c048b.yaml @ b'33d9cc8468f89063934a58c08eb9d04e09aae895'

- In this release the main repository was moved off of OpenStack provided
  infrastructure and onto github at
  https://github.com/jamielennox/requests-mock. OpenStack has been a great
  home for the project however requests-mock is a general python project with
  no specific relationship to OpenStack and the unfamiliar infrastructure was
  limiting contributes from the wider community.


.. _requests-mock_1.3.0:

1.3.0
=====

.. _requests-mock_1.3.0_New Features:

New Features
------------

.. releasenotes/notes/additional-matcher-5c5cd466a6d70080.yaml @ b'aa3e87c4ee8da57b0b71f0a9511af89002a7aa1e'

- Allow specifying an `additional_matcher` to the mocker that will call a function to allow a user to add their own custom request matching logic.


.. _requests-mock_1.1.0:

1.1.0
=====

.. _requests-mock_1.1.0_Prelude:

Prelude
-------

.. releasenotes/notes/Add-called_once-property-a69546448cbd5542.yaml @ b'0c6e567ec77681178e461c2994db16fa81aea4a8'

Add a called_once property to the mockers.


.. releasenotes/notes/case-insensitive-matching-a3143221359bbf2d.yaml @ b'1b08dcc70557b2d58c56a923e6d3176c2b64a14f'

It is now possible to make URL matching and request history not lowercase the provided URLs.


.. releasenotes/notes/fixture-extras-699a5b5fb5bd6aab.yaml @ b'6df03ed3d03d05f606bff28764e72bc0574333b7'

Installing the requirements for the 'fixture' contrib package can now be done via pip with `pip install requests-mock[fixture]`


.. _requests-mock_1.1.0_New Features:

New Features
------------

.. releasenotes/notes/Add-called_once-property-a69546448cbd5542.yaml @ b'0c6e567ec77681178e461c2994db16fa81aea4a8'

- A called_once property was added to the adapter and the mocker. This gives us an easy way to emulate mock's assert_called_once.

.. releasenotes/notes/case-insensitive-matching-a3143221359bbf2d.yaml @ b'1b08dcc70557b2d58c56a923e6d3176c2b64a14f'

- You can pass case_sensitive=True to an adapter or set `requests_mock.mock.case_sensitive = True` globally to enable case sensitive matching.

.. releasenotes/notes/fixture-extras-699a5b5fb5bd6aab.yaml @ b'6df03ed3d03d05f606bff28764e72bc0574333b7'

- Added 'fixture' to pip extras so you can install the fixture requirements with `pip install requests-mock[fixture]`


.. _requests-mock_1.1.0_Upgrade Notes:

Upgrade Notes
-------------

.. releasenotes/notes/case-insensitive-matching-a3143221359bbf2d.yaml @ b'1b08dcc70557b2d58c56a923e6d3176c2b64a14f'

- It is recommended you add `requests_mock.mock.case_sensitive = True` to your base test file to globally turn on case sensitive matching as this will become the default in a 2.X release.


.. _requests-mock_1.1.0_Bug Fixes:

Bug Fixes
---------

.. releasenotes/notes/case-insensitive-matching-a3143221359bbf2d.yaml @ b'1b08dcc70557b2d58c56a923e6d3176c2b64a14f'

- Reported in bug \#1584008 all request matching is done in a case insensitive way, as a byproduct of this request history is handled in a case insensitive way. This can now be controlled by setting case_sensitive to True when creating an adapter or globally.

