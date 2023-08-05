# photo-gen
A rewrite of my go photo gallery generator to Python, because I'll work faster in it. Golang was awesome, but I think it is more important for me to use the little time I have on actually implementing new features rather than figuring out how to do it in Golang.

## Getting started
1. Install the package: `pip install photo-gen`
2. Create a folder for your new photo site: `mkdir ~/photo-site && cd ~/photo-site`
3. Initialise the project: `python -m photo-gen init`
4. Add some photos: go into the photos directory, add one folder per gallery you
   want and add photos inside it.
5. Generate it: `python -m photo-gen build`
6. Done.

The result will be written to output, don't make any changes there because it
will be overwritten each time you run build. You should modify config.yml to
match your domain and desires. Because the default is my domai nname. And if you
want to change the CSS or templates you'll find them in assets. I use the
template engine Jinja2. 
   
