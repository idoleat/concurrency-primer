import json
import sys

# This is not idiot-proof. Meaning that if you use scope with rules not defined here,
# you will have </div>s generated but no <div>s
def replace(chap):
    chap['Chapter']['content'] = chap['Chapter']['content'].replace(":::horizontal", "<div class=\"hori_container\">\n")
    # add nother rule by changing name after ::: and class name

    # must be the last one
    chap['Chapter']['content'] = chap['Chapter']['content'].replace(":::", "</div>")

def travers(chapters):
    for chap in chapters:
        replace(chap)
        if len(chap['Chapter']['sub_items']) != 0 :
            travers(chap['Chapter']['sub_items'])

if __name__ == '__main__':
    if len(sys.argv) > 1: # we check if we received any argument
        if sys.argv[1] == "supports":
            # then we are good to return an exit status code of 0, since the other argument will just be the renderer's name
            sys.exit(0)

    # load both the context and the book representations from stdin
    context, book = json.load(sys.stdin)

    travers(book['sections'])

    # we are done with the book's modification, we can just print it to stdout,
    print(json.dumps(book))
