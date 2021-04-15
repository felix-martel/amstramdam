import flask


class Flask(flask.Flask):
    jinja_options = flask.Flask.jinja_options.copy()
    jinja_options.update(
        dict(
            variable_start_string="[[",
            variable_end_string="]]",
        )
    )
