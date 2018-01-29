/**
 * Created by xiezhigang on 17/2/21.
 */
const gulp = require('gulp');
// gulp-sourcemaps 处理JavaScript时生成SourceMap
const sourcemaps = require('gulp-sourcemaps');
// gulp-uglify 丑化／压缩js文件
const uglify = require('gulp-uglify');
// gulp-concat 合并文件
const concat = require('gulp-concat');
// gulp-clean-css 压缩css
const cleancss = require("gulp-clean-css");
// gulp-html-replace 替代html中的构建块
const htmlreplace = require("gulp-html-replace");
// del 删除文件或目录
const del = require("del");
// gulp-rev 把静态文件名改成hash的形式
const rev = require("gulp-rev");
// gulp-rev-collector 到线上环境前 用来配合gulp-rev使用 替换HTML中的路径
const collector = require("gulp-rev-collector");

gulp.task("clean:prod", function () {
    return del([
        "static/prod"
    ])
});

// 压缩／哈希公共资源的libs下的js文件
gulp.task("base_lib_js", function () {
    return gulp.src([
        "static/common/libs/jquery.min.js",
        "static/common/libs/bootstrap/js/bootstrap.min.js",
        "static/common/libs/boostratp-datetimepicker/js/bootstrap-datetimepicker.min.js",
        "static/common/libs/boostratp-datetimepicker/js/locales/bootstrap-datetimepicker.zh-CN.js",
        "static/common/libs/bootstrap-validator/js/bootstrapValidator.min.js",
        "static/common/libs/bootstrap-validator/js/language/zh_CN.js",
        "static/common/libs/city-picker/js/cityData.js",
        "static/common/libs/city-picker/js/cityPicker.js",
        "static/common/libs/select2/js/select2.js",
        "static/common/libs/select2/js/i18n/zh-CN.js",
        "static/common/libs/jquery.qrcode.min.js",
        "static/common/libs/metisMenu.min.js",
        "static/common/libs/sb-admin-2.js",
        "static/common/libs/raphael.min.js",
        "static/common/libs/highcharts.js",
        "static/common/libs/exporting.js"
    ]).pipe(sourcemaps.init())
        .pipe(uglify())
        .pipe(concat("base_libs.min.js"))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest("static/prod/js"))
});
gulp.task("hash:base_lib_js", ["base_lib_js"], function () {
    return gulp.src([
        "static/prod/js/base_libs.min.js"
    ]).pipe(rev())
        .pipe(gulp.dest("static/prod/js"))
        .pipe(rev.manifest())
        .pipe(gulp.dest("static/prod/rev/js"))
});

gulp.task("base_common_js", function () {
    return gulp.src([
        "static/common/js/init_time.js",
        "static/common/js/clickActive.js",
        "static/common/js/tbody_noData.js",
        "static/common/js/navigate.js",
        "static/common/js/industry.js",
        "static/common/js/job.js",
        "static/common/js/download.js"
    ]).pipe(sourcemaps.init())
        .pipe(uglify())
        .pipe(concat("base_common.min.js"))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest("static/prod/js"))
});


gulp.task("hash:base_common_js", ["base_common_js"], function () {
    return gulp.src([
        "static/prod/js/base_common.min.js"
    ]).pipe(rev())
        .pipe(gulp.dest("static/prod/js"))
        .pipe(rev.manifest())
        .pipe(gulp.dest("static/prod/rev/js"))
});

// 压缩／哈希公共资源的common下的css文件
gulp.task("base_common_css", function () {
    return gulp.src([
        "static/common/css/metisMenu.min.css",
        "static/common/css/sb-admin-2.css"
    ]).pipe(concat("base_common.min.css"))
        .pipe(cleancss())
        .pipe(gulp.dest("static/prod/css"))
});

gulp.task("base_lib_css",function () {
    return gulp.src([
        "static/common/libs/bootstrap/css/bootstrap.min.css",
        "static/common/font-awesome/css/font-awesome.min.css",
        "static/common/libs/boostratp-datetimepicker/css/bootstrap-datetimepicker.min.css",
        "static/common/libs/bootstrap-fileinput/css/fileinput.min.css",
        "static/common/libs/bootstrap-validator/css/bootstrapValidator.min.css",
        "static/common/libs/city-picker/css/cityPicker.css",
        "static/common/libs/select2/css/select2.min.css"
    ]).pipe(concat("base_libs.min.css"))
        .pipe(cleancss())
        .pipe(gulp.dest("static/prod/css"))
});

gulp.task("hash:base_common_css", ["base_common_css"], function () {
    return gulp.src([
        "static/prod/css/base_common.min.css"
    ]).pipe(rev())
        .pipe(gulp.dest("static/prod/css"))
        .pipe(rev.manifest())
        .pipe(gulp.dest("static/prod/rev/css"))
});

gulp.task("hash:base_lib_css", ["base_lib_css"], function () {
    return gulp.src([
        "static/prod/css/base_libs.min.css"
    ]).pipe(rev())
        .pipe(gulp.dest("static/prod/css"))
        .pipe(rev.manifest())
        .pipe(gulp.dest("static/prod/rev/css"))
});

gulp.task("official_css", function () {
    return gulp.src([
        "static/official/css/style.css"
    ]).pipe(concat("official.min.css"))
        .pipe(cleancss())
        .pipe(gulp.dest("static/prod/css"))
});

gulp.task("hash:official_css", ["official_css"], function () {
    return gulp.src([
        "static/prod/css/official.min.css"
    ]).pipe(rev())
        .pipe(gulp.dest("static/prod/css"))
        .pipe(rev.manifest())
        .pipe(gulp.dest("static/prod/rev/css"))
});

// 生成hash文件
gulp.task("common:control", ["hash:base_lib_js", "hash:base_lib_css", "hash:base_common_js", "hash:base_common_css", "hash:official_css"], function () {
    return gulp.src([
        "static/prod/rev/js/*.json", "templates/*/base.html"
    ]).pipe(collector({
        replaceReved: true
    })).pipe(gulp.dest(function (file) {
        return file.base;
    }))
});

gulp.task("official:html:replace", function () {
    var tpl_js = '<script type="text/javascript" src="%s" defer></script>';
    var tpl_css = '<link rel="stylesheet" href="%s">';

    return gulp.src("templates/official/base.html").pipe(htmlreplace({
        "lib_js": {
            "src": "/static/prod/js/base_libs.min.js",
            "tpl": tpl_js
        },
        "common_js": {
            "src": "/static/prod/js/base_common.min.js",
            "tpl": tpl_js
        },
        // "lib_css": {
        //     "src": "/static/prod/css/base_libs.min.css",
        //     "tpl": tpl_css
        // },
        "common_css": {
            "src": "/static/prod/css/base_common.min.css",
            "tpl": tpl_css
        },
        "official_css": {
            "src": "/static/prod/css/official.min.css",
            "tpl": tpl_css
        }
    })).pipe(gulp.dest("templates/official/"))
});

gulp.task("dist:html:replace", function () {
    var tpl = '<script type="text/javascript" src="%s" defer></script>';

    return gulp.src("templates/distributor/base.html").pipe(htmlreplace({
        "lib_js": {
            "src": "/static/prod/js/base_libs.min.js",
            "tpl": tpl
        },
        "common_js": {
            "src": "/static/prod/js/base_common.min.js",
            "tpl": tpl
        }
    })).pipe(gulp.dest("templates/distributor/"))
});

gulp.task("bank:html:replace", function () {
    var tpl = '<script type="text/javascript" src="%s" defer></script>';

    return gulp.src("templates/bank/base.html").pipe(htmlreplace({
        "lib_js": {
            "src": "/static/prod/js/base_libs.min.js",
            "tpl": tpl
        },
        "common_js": {
            "src": "/static/prod/js/base_common.min.js",
            "tpl": tpl
        }
    })).pipe(gulp.dest("templates/bank/"))
});

gulp.task("merchant:html:replace", function () {
    var tpl = '<script type="text/javascript" src="%s" defer></script>';

    return gulp.src("templates/official/base.html").pipe(htmlreplace({
        "lib_js": {
            "src": "/static/prod/js/base_libs.min.js",
            "tpl": tpl
        },
        "common_js": {
            "src": "/static/prod/js/base_common.min.js",
            "tpl": tpl
        }
    })).pipe(gulp.dest("templates/merchant/"))
});

gulp.task('clean', ["clean:prod"]);

gulp.task('common', ["base_lib_js", "base_common_js", "base_lib_css", "base_common_css", "official_css",
    "hash:base_lib_js", "hash:base_lib_css", "hash:base_common_js", "hash:base_common_css", "hash:official_css",
    "common:control"]);

gulp.task('replace', ["official:html:replace"]);
// gulp.task('replace', ["official:html:replace", "bank:html:replace", "dist:html:replace", "merchant:html:replace"]);
