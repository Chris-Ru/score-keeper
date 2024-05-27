from flask import Flask, render_template, url_for, request, redirect, flash, render_template_string
from routing import *
import sqlite3

if __name__ == "__main__":
    #runs the application on the repl development server
        init_db()
        app.run(debug=True)