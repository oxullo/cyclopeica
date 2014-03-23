#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from flask import Flask, jsonify

app = Flask(__name__)

phrases = [line.strip() for line in open('phrases.txt').read().split('\n')]

@app.route('/')
def phraseize():
    return jsonify({'phrase': random.choice(phrases)})

if __name__ == '__main__':
    app.run(debug=True)
