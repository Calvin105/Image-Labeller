import os
from shutil import move
from PIL.Image import registered_extensions

from classifier import app, LABELS, ZFILL, relative_extraction, static_extraction, START_NUM
from classifier.models import ImageModel
from flask import url_for, render_template, request, redirect, flash
from typing import List


labels_count = {x: 0 for x in LABELS.keys()}

purified_files = []
file_ls = os.listdir(relative_extraction)
for x in file_ls:
    name, extension = os.path.splitext(x)
    if name == "" or extension == "" or extension not in registered_extensions():
        continue
    purified_files.append(x)

image_models: List[ImageModel] = []
for i in range(len(purified_files)):
    image_model = ImageModel(filepath=os.path.join(relative_extraction, purified_files[i]))
    image_models.append(image_model)


def get_image(model: ImageModel):
    return "static/"+os.path.join(static_extraction, model.filename)


def get_log_instance(model: ImageModel):
    if model.label != "None":
        return f"{model.label}/{model.chg_filename}{model.extension}"
    if model.chg_filename:
        return model.chg_filename + model.extension
    return model.label


def commit_changes():
    ls = []
    cwd = os.getcwd()
    for model in image_models:
        name = model.chg_filename
        label = LABELS[model.label]
        if not model.chg_filename:
            name = model.filename
        if label == None:
            continue
        else:
            label = label[1]
        ls.append([f"{cwd}/{model.filepath}", f"{cwd}/classifier/static/{label}/{name}{model.extension}"])

    for fro, to in ls:
        move(fro, to)


@app.route("/", methods=["GET", "POST"], defaults={"page" : 1})
@app.route("/<int:page>", methods=["GET", "POST"])
def home(page):
    if page > len(image_models):
        return render_template("404.html")

    if request.args.get("page"):
        page = request.args.get("page")

    if request.form.get("send") == "submit":
        add_label = request.form.get("add-label")
        new_path = f"{os.getcwd()}/classifier/static/picture/{add_label.lower()}"

        if add_label:
            if os.path.exists(new_path):
                flash(f"{add_label} is an existing directory", "label-error")
            else:
                flash(f"{add_label} label added to directory", "label-success")
                os.makedirs(new_path)
                LABELS[add_label] = ["static", f"picture/{add_label.lower()}"]
                START_NUM[add_label] = 0
                labels_count[add_label] = 0

        else:
            flash(f"Please provide a label", "label-error")

    if request.form.get("stats") == "stats":
        return redirect(url_for("commit", page=page))

    if request.form.get("commit") == "commit":
        commit_changes()
        return redirect("finish")

    if request.form.get("post-action") == "Next":
        label = request.form.get("label-action")
        filename = request.form.get("filename-action")

        # Check for replica filename
        replica = False
        if filename != "" and not filename.isdigit():
            for model in image_models:
                if model.chg_filename == filename or model.name == filename:
                    replica = True
                    break

        if not replica:

            # Create name
            name = ""
            if label != "None":
                name = str(labels_count[label] + START_NUM[label]).zfill(ZFILL)
            if filename != "" and not filename.isdigit():
                name = filename
            image_models[page-1].chg_filename = name
            image_models[page-1].label = label

            if filename == "" or filename.isdigit():
                labels_count[image_models[page-1].label] += 1

            if page == len(image_models):
                return redirect(url_for("commit", page=len(image_models)))

            return redirect(url_for("home", page=page+1))

        else:
            flash("Replica filename detected", "filename-error")

    elif request.form.get("post-action") == "Back" and page-1 != 0:
        if image_models[page-2].chg_filename.isdigit():
            labels_count[image_models[page-2].label] -= 1
            
        return redirect(url_for("home", page=page-1))

    logs = []
    for i in range(5):
        if page-i-1 < 1:
            logs.append("-")
        else:
            logs.append(get_log_instance(image_models[page-i-2]))

    return render_template("main.html",
                            img_file=get_image(image_models[page-1]),
                            img=image_models[page-1],
                            image_number=f"{page} / {len(image_models)}",
                            labels=list(LABELS.keys()),
                            logs=logs,
                            static_path=static_extraction)


def count_labels():
    x = {k:0 for k in LABELS.keys()}
    for model in image_models:
        x[model.label] += 1
    return x


@app.route("/end", methods=["GET", "POST"])
def commit():
    page = int(request.args.get("page"))
    if request.form.get("back") == "back":
        return redirect(url_for("home", page=page))

    if request.form.get("commit") == "commit":
        commit_changes()
        return redirect("finish")

    logs = []
    truncation = 30 < len(image_models)
    images_length = len(image_models)
    for i in range(30):
        if images_length-i < 1:
            logs.append("-")
        elif i == 29 and truncation:
            logs.append("...")
        else:
            logs.append(get_log_instance(image_models[images_length-i-1]))
    
    length = len(LABELS.keys())
    cols = [[i, 10] for i in range(length//10)]
    cols.append([length//10, length%10])
    total = len(image_models)
    labelled = sum(labels_count.values()) - labels_count["None"]
    unlabelled = total - labelled
    stats = [total, labelled, unlabelled]

    return render_template("commit.html",
                            logs=logs,
                            labels=list(LABELS.keys()),
                            label_loop=cols,
                            category_count=count_labels(),
                            stats=stats)


@app.route("/finish")
def finish():
    return render_template("finish.html")


@app.errorhandler(404)
def page_not_found(_):
    return render_template("404.html")
