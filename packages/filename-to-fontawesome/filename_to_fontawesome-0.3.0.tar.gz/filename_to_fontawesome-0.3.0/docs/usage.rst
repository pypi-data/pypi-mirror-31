=====
Usage
=====

To use Filename to FontAwesome in a project

*Standard Use*:
::
    In [1]: from filename_to_fontawesome.filename_to_fontawesome import ftfa

    In [2]: ftfa_ = ftfa()

    In [3]: print(ftfa_.getfontawesome("toto.py"))
    far fa-file-code

    In [4]: print(ftfa_.getfontawesome(""))
    far fa-file


*Markup output*:
::
    In [1]: from filename_to_fontawesome.filename_to_fontawesome import ftfa

    In [2]: ftfa_ = ftfa(markup=True, fontversion="v4")

    In [3]: print(ftfa_.getfontawesome("toto.docx"))
    <i class="fa fa-file-word-o" aria-hidden="true"></i>

    In [4]: print(ftfa_.getfontawesome("toto.unknowable"))
    <i class="fa fa-file-o" aria-hidden="true"></i>

*Unicode output*:
::
    In [1]: from filename_to_fontawesome.filename_to_fontawesome import ftfa

    In [2]: ftfa_ = ftfa(markup=False, fontversion="v5solid", unicodeoutput=True)

    In [3]: print(ftfa_.getfontawesome("toto.py"))
    f1c9

    In [4]: print(ftfa_.getfontawesome("toto.unknowable"))
    f15b

*Mime type input*:
::
    In [1]: from filename_to_fontawesome.filename_to_fontawesome import ftfa

    In [2]: ftfa_ = ftfa(markup=True, fontversion="v5solid")

    In [3]: print(ftfa_.mimetfa("text/plain"))
    <i class="fas fa-file-text"></i>


