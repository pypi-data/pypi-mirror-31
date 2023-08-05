import os
import sys
from flask import Flask, render_template, request, session
from werkzeug import secure_filename
import tempfile
from argparse import Namespace

# strange way to do the imports, but hey
from clermontpcr import clermontpcr
# check that the import works
print(clermontpcr.PcrHit)

app = Flask(__name__)
# app.secret_key = 'crytographyisnotmystrongsuit'
app.secret_key = os.urandom(24)

#  set the max file size to 20mb.  If an ecoli fasta is
#    larger than this, then its probably not an e coli
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024


def default_stream_factory(total_content_length, filename, content_type, content_length=None):
    """The stream factory that is used per default."""
    # if total_content_length > 1024 * 500:
    #    return TemporaryFile('wb+')
    # return BytesIO()
    return TemporaryFile('wb+')

def get_tmpfile_path():
    return os.path.join(tempfile.gettempdir(), "tmp.fasta")


@app.route("/", methods=['GET','POST'])
def index():
    session["FINISHED"] = False
    session["LOADED"] = False
    file_content = [""]
    # return render_template("template.html", content=content) #
    if request.method == 'POST':
        print(request.form['submit'])
        if request.form['submit'] == "Get Clermont Phylotype!" :
            # for secure filenames. Read the documentation.
            file = request.files['myfile']
            filename = secure_filename(file.filename)
            tmpdir = tempfile.gettempdir()
            print(tmpdir)
            # tmpfile = os.path.join(tmpdir, filename)
            tmpfile = get_tmpfile_path()
            file.save(tmpfile)
            with open(tmpfile) as f:
                file_content = f.read().split("\n")
            teaser = "\n".join(file_content[0:7])
            addn_lines = len(file_content) - 7
            if addn_lines < 0:
                addn_lines = 0
            header = "Here is the first bit of your file:"
            session["LOADED"] = True

            ###   Now lets run the main function
            if os.path.isfile(tmpfile):
                print(tmpfile)
                results, profile  = runcler(
                    contigsfile=tmpfile,
                    #ignore_control=request.form.get('allowcontrolfails'),
                    ignore_control=False,
                    partial=request.form.get('allowpartial')
                )
            else:
                raise ValueError("clicky clicky clicky;  select a file first")
            ###
            return render_template(
                'alt.html',
                header=header,
                content=teaser,
                results=results,
                profile=profile,
                nlines="...and %d more lines" % addn_lines
            )
        else:
            pass
    else:
        return render_template("alt.html")

def runcler(contigsfile, ignore_control=False, partial=False):
    # prepare args
    args = Namespace(contigs=contigsfile,
                     ignore_control=ignore_control, partial=partial)
    try:
        results, profile  = clermontpcr.main(args)
    except Exception as e:
        if e is AttributeError:
            results = "Deploy error!"
        else:
            print(e)
            results = str("Control fail!  Are you sure this is E. coli? " +
                          "Please contact the support team")
        profile = ""
    return (results, profile)

if __name__ == "__main__":
    app.run(debug=True, port=5957)
