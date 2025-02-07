"use strict";
var fs = require('fs'),
    gulp = require('gulp'),
    concat = require('gulp-concat'),
    livereload = require('gulp-livereload'),
    cleanCss = require('gulp-clean-css'),
    rename = require('gulp-rename'),
    sass = require('gulp-sass')(require('sass')),
    watch = require('gulp-watch'),
    postcss = require('gulp-postcss'),
    json = JSON.parse(fs.readFileSync('./package.json')),
    terser = require('gulp-terser');

let prefix;
import('gulp-autoprefixer').then((module) => {
    prefix = module.default;
}).catch((error) => {
    console.error('Error importing module:', error);
});

var config = (function () {
    var appName = json.name;

    var path = {
        app: './' + appName,
        npm: './node_modules/',
        assets: './' + appName + '/assets',
        static: './' + appName + '/static',
        staticfiles: './staticfiles'
    };

    return {
        path: path,
        scss: {
            input: [
                path.assets + '/scss/style.scss',
                path.npm + '/datatables.net-buttons-dt/css/buttons.dataTables.css',
                path.npm + '/datatables.net-dt/css/jquery.dataTables.css',
            ],
            include: [
                './node_modules/bootstrap-sass/assets/stylesheets',
                './node_modules/@fortawesome/fontawesome-free/scss',
                path.assets + '/scss/'
            ],
            output: {
                dir: path.static + "/css",
                filename: 'style.css'
            },        
            watch: [
                path.assets + '/scss/**.scss'
            ]
        },
        images: {
            input: [
                path.npm + '/datatables.net-dt/images/sort*.*'
            ],
            output: path.static + "/images"
        },
        icons: {
            input: [
                './node_modules/@fortawesome/fontawesome-free/webfonts/**.*'
            ],
            output: path.static + "/webfonts"
        },
        script: {
            input: [
                './node_modules/jquery/dist/jquery.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/tab.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/transition.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/dropdown.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/tooltip.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/collapse.js',
                path.assets + '/js/*.js',
                path.npm + '/datatables.net/js/jquery.dataTables.js',
                // path.npm + 'datatables.net-bs4/js/dataTables.bootstrap4.js',
                path.npm + '/datatables.net-dt/js/dataTables.dataTables.js',
                path.npm + '/datatables.net-buttons/js/dataTables.buttons.js',
                path.staticfiles + '/ajax_datatable/js/utils.js',
                path.app + '/monitorings/static/monitorings/monitorings_datatables.js',
                path.app + '/monitorings/static/monitorings/monitoring_cases_datatables.js',
                path.app + '/monitorings/static/monitorings/monitoring_assign_select_count.js',
            ],
            output: {
                dir: path.static + "/js",
                filename: 'script.js'
            },
            watch: [
                path.assets + '/js/*.js'
            ]
        }
    };
}());

gulp.task('icons', function () {
    return gulp.src(config.icons.input)
        .pipe(gulp.dest(config.icons.output));
});

gulp.task('images', function () {
    return gulp.src(config.images.input)
        .pipe(gulp.dest(config.images.output));
});

gulp.task('js', function () {
    return gulp.src(config.script.input)
        .pipe(concat(config.script.output.filename))
        .pipe(gulp.dest(config.script.output.dir))
        .pipe(livereload())
        .pipe(terser())
        .pipe(rename({extname: '.min.js'}))
        .pipe(gulp.dest(config.script.output.dir))
        .pipe(livereload());
});

gulp.task('scss', function () {
   return gulp.src(config.scss.input)
        .pipe(sass({
            style: "expanded",
            includePaths: config.scss.include
        }))
        .pipe(prefix())
        .pipe(concat(config.scss.output.filename))
        .pipe(gulp.dest(config.scss.output.dir))
        .pipe(livereload())
        .pipe(cleanCss())
        .pipe(rename({extname: '.min.css'}))
        .pipe(gulp.dest(config.scss.output.dir))
        .pipe(livereload());
});

// Rerun the task when a file changes
// gulp.task('watch', function () {
//     livereload.listen();
//     config.scss.watch.forEach(function (path) {
//         gulp.watch(path, ['scss']);
//     });
//     config.script.watch.forEach(function (path) {
//         gulp.watch(path, ['js']);
//     });
// });


gulp.task('build', gulp.series('images', 'icons', 'js', 'scss'));

// gulp.task('default', gulp.series('build', 'watch'));
gulp.task('default', gulp.series('build'));
