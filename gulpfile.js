"use strict";
var fs = require('fs');

var gulp = require('gulp'),
    cleanCss = require('gulp-clean-css'),
    concat = require('gulp-concat'),
    livereload = require('gulp-livereload'),
    postcss = require('gulp-postcss'),
    rename = require('gulp-rename'),
    sass = require('gulp-sass'),
    uglify = require('gulp-uglify');

var autoprefixer = require('autoprefixer')
var json = JSON.parse(fs.readFileSync('./package.json'));

var config = (function () {
    var appName = json.name;

    var path = {
        assets: './' + appName + '/assets',
        static: './' + appName + '/static'
    };

    return {
        path: path,
        scss: {
            input: path.assets + '/scss/style.scss',
            include: [
                './node_modules/bootstrap-sass/assets/stylesheets',
                './node_modules/font-awesome/scss',
                path.assets + '/scss/'
            ],
            output: path.static + "/css",
            watch: [
                path.assets + '/scss/**.scss'
            ]
        },
        icons: {
            input: [
                './node_modules/font-awesome/fonts/**.*'
            ],
            output: path.static + "/fonts"
        },
        script: {
            input: [
                './node_modules/jquery/dist/jquery.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/tab.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/transition.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/dropdown.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/tooltip.js',
                './node_modules/bootstrap-sass/assets/javascripts/bootstrap/collapse.js',
                path.assets + '/js/*.js'
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

gulp.task('js', function () {
    return gulp.src(config.script.input)
        .pipe(concat(config.script.output.filename))
        .pipe(gulp.dest(config.script.output.dir))
        .pipe(livereload())
        .pipe(uglify())
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
        .pipe(postcss([
            autoprefixer()
        ]))
        .pipe(gulp.dest(config.scss.output))
        .pipe(livereload())
        .pipe(rename({extname: '.min.css'}))
        .pipe(cleanCss())
        .pipe(gulp.dest(config.scss.output))
        .pipe(livereload());
});

// Rerun the task when a file changes
gulp.task('watch', function () {
    livereload.listen();
    config.scss.watch.forEach(function (path) {
        gulp.watch(path, ['scss']);
    });
    config.script.watch.forEach(function (path) {
        gulp.watch(path, ['js']);
    });
});


gulp.task('build', gulp.series('icons', 'js', 'scss'));

gulp.task('default', gulp.series('build', 'watch'));
