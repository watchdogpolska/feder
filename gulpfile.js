"use strict";

const fs = require("fs");
const { src, dest, series, watch } = require("gulp");
const concat = require("gulp-concat");
const livereload = require("gulp-livereload");
const cleanCss = require("gulp-clean-css");
const rename = require("gulp-rename");
const sass = require("gulp-sass")(require("sass"));
const postcss = require("gulp-postcss");
const autoprefixer = require("autoprefixer");
const terser = require("gulp-terser");

const json = JSON.parse(fs.readFileSync("./package.json"));

const config = (() => {
  const appName = json.name;

  const path = {
    app: "./" + appName,
    npm: "./node_modules/",
    assets: "./" + appName + "/assets",
    static: "./" + appName + "/static",
    staticfiles: "./staticfiles",
  };

  return {
    path,
    scss: {
      input: [
        // path.npm + "/@fortawesome/fontawesome-free/css/fontawesome.css",
        // path.npm + "/@fortawesome/fontawesome-free/css/solid.css",
        // path.npm + "/@fortawesome/fontawesome-free/css/regular.css",
        // path.npm + "/@fortawesome/fontawesome-free/css/brands.css",
        path.npm + "/@fortawesome/fontawesome-free/css/all.css",
        path.assets + "/scss/style.scss",
        path.npm + "/datatables.net-buttons-dt/css/buttons.dataTables.css",
        path.npm + "/datatables.net-dt/css/jquery.dataTables.css",
      ],
      include: [
        path.npm,
        "./node_modules/bootstrap-sass/assets/stylesheets",
        "./node_modules/@fortawesome/fontawesome-free/scss",
        path.assets + "/scss/",
        path.staticfiles,
      ],
      output: {
        dir: path.static + "/css",
        filename: "style.css",
      },
      watch: [path.assets + "/scss/**.scss"],
    },
    images: {
      input: [path.npm + "/datatables.net-dt/images/sort*.*"],
      output: path.static + "/images",
    },
    icons: {
      input: ["./node_modules/@fortawesome/fontawesome-free/webfonts/**.*"],
      output: path.static + "/webfonts",
    },
    script: {
      input: [
        "./node_modules/jquery/dist/jquery.js",
        "./node_modules/bootstrap-sass/assets/javascripts/bootstrap/tab.js",
        "./node_modules/bootstrap-sass/assets/javascripts/bootstrap/transition.js",
        "./node_modules/bootstrap-sass/assets/javascripts/bootstrap/dropdown.js",
        "./node_modules/bootstrap-sass/assets/javascripts/bootstrap/tooltip.js",
        "./node_modules/bootstrap-sass/assets/javascripts/bootstrap/collapse.js",
        // Core DataTables (ensure datatables.net is installed)
        path.npm + "/datatables.net/js/jquery.dataTables.js",
        // DataTables styling + extras
        path.npm + "/datatables.net-dt/js/dataTables.dataTables.js",
        path.npm + "/datatables.net-buttons/js/dataTables.buttons.js",
        // Project JS
        path.assets + "/js/*.js",
        path.staticfiles + "/ajax_datatable/js/utils.js",
        path.app + "/monitorings/static/monitorings/monitorings_datatables.js",
        path.app + "/monitorings/static/monitorings/monitoring_cases_datatables.js",
        path.app + "/monitorings/static/monitorings/monitoring_assign_select_count.js",
      ],
      output: {
        dir: path.static + "/js",
        filename: "script.js",
      },
      watch: [path.assets + "/js/*.js"],
    },
  };
})();

// ---- Tasks ----
function icons() {
  return src(config.icons.input, { encoding: false })
    .pipe(dest(config.icons.output));
}

function images() {
  return src(config.images.input, { encoding: false })
    .pipe(dest(config.images.output));
}

function js() {
  return src(config.script.input, { allowEmpty: false })
    .pipe(concat(config.script.output.filename))
    .pipe(dest(config.script.output.dir))
    .pipe(livereload())
    .pipe(terser())
    .pipe(rename({ extname: ".min.js" }))
    .pipe(dest(config.script.output.dir))
    .pipe(livereload());
}

function scss() {
  return src(config.scss.input, { allowEmpty: false })
    .pipe(
      sass({
        style: "expanded",
        includePaths: config.scss.include,
      }).on("error", sass.logError)
    )
    .pipe(postcss([autoprefixer()]))
    .pipe(concat(config.scss.output.filename))
    .pipe(dest(config.scss.output.dir))
    .pipe(livereload())
    .pipe(cleanCss())
    .pipe(rename({ extname: ".min.css" }))
    .pipe(dest(config.scss.output.dir))
    .pipe(livereload());
}

function watcher() {
  livereload.listen();
  config.scss.watch.forEach((p) => watch(p, scss));
  config.script.watch.forEach((p) => watch(p, js));
}

// Public task compositions
const build = series(images, icons, js, scss);

exports.icons = icons;
exports.images = images;
exports.js = js;
exports.scss = scss;
exports.watch = watcher;
exports.build = build;
exports.default = build;
