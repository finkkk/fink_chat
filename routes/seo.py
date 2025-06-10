# routes/system.py
from flask import Blueprint

seo_bp = Blueprint('seo', __name__)

# ====== SEO 文件服务 ======
@seo_bp.route("/robots.txt")
def robots():
    return seo_bp.send_static_file("robots.txt")

@seo_bp.route("/sitemap.xml")
def sitemap():
    return seo_bp.send_static_file("sitemap.xml")