from __future__ import annotations

from functools import wraps
import json
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from digit_recognizer.auth import create_user, verify_user
from digit_recognizer.config import DATABASE_PATH, MODEL_PATH
from digit_recognizer.database import add_history, get_history, init_db
from digit_recognizer.predictor import Predictor, PredictorUnavailable


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "digit-recognition-coursework-dev-key"

    Path("data").mkdir(exist_ok=True)
    init_db(DATABASE_PATH)

    try:
        app.predictor = Predictor(MODEL_PATH)
        app.model_error = None
    except PredictorUnavailable as exc:
        app.predictor = None
        app.model_error = str(exc)

    @app.context_processor
    def inject_globals():
        return {
            "current_user": session.get("username"),
            "model_ready": app.predictor is not None,
            "model_error": app.model_error,
        }

    @app.route("/")
    def root():
        return redirect(url_for("workspace"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if len(username) < 3 or len(password) < 6:
                flash("用户名至少 3 位，密码至少 6 位。")
            elif create_user(DATABASE_PATH, username, password):
                flash("注册成功，请登录。")
                return redirect(url_for("login"))
            else:
                flash("用户名已存在。")
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = verify_user(DATABASE_PATH, username, password)
            if user:
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("workspace"))
            flash("用户名或密码错误。")
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("workspace"))

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped

    @app.route("/workspace")
    def workspace():
        return render_template("index.html")

    @app.route("/history")
    @login_required
    def history():
        rows = get_history(DATABASE_PATH, session["user_id"])
        return render_template("history.html", rows=rows)

    @app.route("/about")
    def about():
        return render_template("about.html")

    @app.route("/api/predict", methods=["POST"])
    def api_predict():
        if app.predictor is None:
            return jsonify({"error": app.model_error or "模型未加载，请先运行 python train.py"}), 503

        payload = request.get_json(silent=True) or {}
        pixels = payload.get("pixels")
        thumbnail = payload.get("thumbnail", "")
        if not isinstance(pixels, list) or len(pixels) != 28 * 28:
            return jsonify({"error": "pixels 必须是长度为 784 的灰度数组。"}), 400

        try:
            result = app.predictor.predict_pixels(pixels)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        if session.get("user_id"):
            add_history(
                DATABASE_PATH,
                user_id=session["user_id"],
                predicted_digit=result["predicted_digit"],
                probabilities_json=json.dumps(result["probabilities"], ensure_ascii=False),
                thumbnail=thumbnail[:120_000],
            )
        return jsonify(result)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5001, debug=False)
