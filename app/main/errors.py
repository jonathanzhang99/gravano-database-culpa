from flask import render_template

from . import main


@main.errorhandler(404)
def handle_404():
    render_template('404.html')