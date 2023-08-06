potypo
======

Spellchecking for translation using .po-files. This is currently work-in-progress.
This project is specifically tailored to be used with django-applications, but
may be used in any project that uses .po-files for translation.

Installation
------------

potypo is available via ``pip3 install potypo``
Note that this is not considered stable and might be subject to massive
changes. Please do use it, and report any problems encountered :)

Configuration
-------------

Configuration is done in a configuration file called ``setup.cfg``. It follows
the configuration file format used in most of the python world, thus it can be
easily used with similar files that are used for other projects, i.e.
``flake8``, ``isort`` or others.

This is an example configuration for potypo.

::

    [potypo]
    # This is the default language of the application, and the language that is
    # translated from. It follows the locale tag naming scheme.
    default_language = en_US

    # This is the directory that contains the .po-files.
    # It follows the structure <lang>/LC_MESSAGES/django{js}.po where <lang> is the
    # language that is translated into.
    locales_dir = /path/to/my/projects/locales

    # This is the directory containing word lists with words that are not included
    # in the corresponding language dictionary, since they are application-specific,
    # uncommon inflections or otherwise special.
    # The wordlists only need to contain uncapitalized words.
    # They should be named according to the language they belong to in the format
    # <lang>.txt, i.e. for the language "en_US", the file should be named
    # "en_US.txt".
    # They can also be placed in the language- or .po-file-directory
    wl_dir = /path/to/my/projects/wordlists

    # For easy CI-Integration, potypo will issue an exit(1) if any errors have been encountered.
    # If there are languages for which this is not wanted, they should be added to this list.
    no_fail =
        fr
        pt_BR

    # Because of how the spell-checking work, some words might be output as "wrong",
    # even though they are correctly spelled. This will for example happen to
    # hyphenated words where a part is not a correct word on its own, abbreviations
    # containing numbers, webpages, …
    # This is a list containing those words, so that they can be filtered.
    edgecase_words =
        add-ons
        MT940
        pre-selected
        myblog.org
        myproject.org-Blog
        myproject.org-Server
        4th

    # Similar to the above edgecase words, there might be complete phrases that are used
    # in a language although not being from that language, i.e. the phrase "powered
    # by" being used in a german text.
    # This is a list containing these phrases, so that they can be filtered.
    phrases =
        powered by

    # This is a list of filters and chunkers to be used by the spell checking
    # process.
    chunkers = enchant.tokenize.HTMLChunker
    filters = PythonFormatFilter,enchant.tokenize.URLFilter,HTMLFilter

Current Work:
-------------
* add config option for languages that should not fail
* enhance README
* find .po-files recursively?
* move this list to issues
* finish setting up testsetup
  * change .po-files
  * set up setup.cfg
  * find out how to start potypo correctly

