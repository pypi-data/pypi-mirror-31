import requests
from flask import Flask
from flask import render_template
from flask_restful import Api
from flask_restful import Resource

app = Flask(__name__)
api = Api(app)


class PostList(Resource):
    def get(self):
        return {"posts": ["BKASKJDKASD"]}


class Post(Resource):
    def get(self, post_path):
        return {"path": post_path, "content": ""}


@app.route("/admin/")
def admin_index():
    return render_template("index.html")


@app.route("/admin/posts/")
def admin_list_posts():
    res = requests.get("http://127.0.0.1:5000/api/posts")
    return render_template("posts.html", **res.json())


api.add_resource(PostList, '/api/posts')
api.add_resource(Post, '/api/posts/<post_path>')


def main():
    app.run(debug=True, threaded=True)


if __name__ == '__main__':
    main()
