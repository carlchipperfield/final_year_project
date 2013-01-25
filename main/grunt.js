/*global module:false*/
module.exports = function (grunt) {

    var SRC_CSS    = 'web/css/',
        SRC_JS     = 'web/js/',
        SRC_JS_LIB = SRC_JS + 'libraries/';

    // Project configuration.
    grunt.initConfig({

        lint: {
            files: [
                'grunt.js',
                SRC_JS + '*.js',
                SRC_JS + 'utils/*.js'
            ]
        },

        // Files to copy to the build directory
        copy: {

            js: {
                files: {

                    'build/app/share/web/js/libraries/jquery-1.8.2.min.js'
                        : SRC_JS_LIB + 'jquery-1.8.2.min.js',

                    'build/app/share/web/js/libraries/angular.min.js'
                        : SRC_JS_LIB + 'angular.min.js',

                    'build/app/share/web/js/libraries/bootstrap.min.js'
                        : 'web/bootstrap/js/bootstrap.min.js',

                    'build/app/share/web/js/source/core/snapshot_upload.js'
                        : SRC_JS + 'core/snapshot_upload.js',

                    'build/app/share/web/js/source/core/snapshots_controller.js'
                        : SRC_JS + 'core/snapshots_controller.js'
                }
            },

            css: {
                files: {
                    'build/app/share/web/css/' : 'web/css/normalize.css',
                    'build/app/share/web/bootstrap/' : 'web/bootstrap/**'
                }
            },

            core: {
                files: {
                    'build/app/share/api/': 'api/**',
                    'build/app/share/python/site-packages/ni/': 'functional/ni/**',
                    'build/app/share/web/': 'web/*',
                    'build/app/share/web/partials/': 'web/partials/*',

                    // Copy the python virtualenv to the build
                    'build/app/python/': 'python/**'
                }
            },

            platform: {
                files: {
                    'build/app/apache2/': 'setup/apache2/**'
                }
            }
        },

        // Src files are concat and minified to the dest file.
        // JS mapping also used for debugging
        // http://www.html5rocks.com/en/tutorials/developertools/sourcemaps/
        'jsmin-sourcemap': {
            core: {

                src: [
                    'source/core/*.js'
                ],
                dest: 'core.min.js',
                destMap: 'core.js.map',
                cwd: 'build/app/share/web/js/'
            }
        },

        sass: {
            core: {
                files: {
                    'build/app/share/web/css/core.css':  [
                        SRC_CSS + 'main_layout.scss',
                        SRC_CSS + 'navigation.scss'
                    ]
                }
            }
        },

        /* The source code should be build,
        which allows for easy distribution */
        compress: {
            main: {
                files: {
                    'build/app.tgz': 'build/**'
                }
            }
        },

        jshint: {
            options: {
                bitwise: true,
                curly: true,
                eqeqeq: true,
                forin: true,
                immed: true,
                indent: 4,
                latedef: true,
                newcap: true,
                noarg: true,
                noempty: true,
                quotmark: 'single',
                undef: true,
                unused: true,
                trailing: true,
                sub: true,
                eqnull: true,
                browser: true,
                jquery: true
            },

            globals: {
                jQuery : true,
                'alert': true,
                'console': true
            }
        },

        watch: {
            gruntfile: {
                files: ['web/**'],
                tasks: ['default']
            }
        }

    });

    // Load third party plugins
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-compress');
    grunt.loadNpmTasks('grunt-sass');
    grunt.loadNpmTasks('grunt-jsmin-sourcemap');

    // Specify tasks
    grunt.registerTask('default', 'lint copy jsmin-sourcemap sass compress');
};