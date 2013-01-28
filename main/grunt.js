/*global module:false*/
module.exports = function (grunt) {

    // Project configuration.
    grunt.initConfig({

        build_dirs: {
            api: 'build/app/share/api',
            web: 'build/app/share/web',
            python: 'build/app/share/python'
        },

        lint: {
            files: [
                'grunt.js',
                'web/js/**'
            ]
        },

        // Files to copy to the build directory
        copy: {

            js: {
                files: {
                    '<%=build_dirs.web%>/js/source/': [
                        'web/js/app.js',
                        'web/js/filters.js',
                        'web/js/directives.js',
                        'web/js/services.js',
                        'web/js/controllers.js'
                    ]
                }
            },

            css: {
                files: {
                    '<%=build_dirs.web%>/css/': [
                        'web/css/normalize.css'
                    ]
                }
            },

            templates: {
                files: {
                    '<%=build_dirs.web%>/': [
                        'web/index.html',
                        'web/partials/**'
                    ]
                }
            },

            lib: {
                files: {
                    '<%=build_dirs.web%>/lib/': [
                        'web/lib/angular/angular.min.js',
                        'web/lib/angular/angular-resource.min.js',
                        'web/lib/jquery/jquery-1.8.2.min.js',
                        'web/lib/bootstrap/css/bootstrap.min.css',
                        'web/lib/bootstrap/js/bootstrap.min.js',
                        'web/lib/bootstrap/img/**'
                    ]
                }
            },

            img: {
                files: {
                    '<%=build_dirs.web%>/img/': [
                        'web/images/cisco.png'
                    ]
                }
            },

            core: {
                files: {
                    // Copy the API
                    '<%=build_dirs.api%>/': 'api/**',

                    // Copy the functional python source
                    '<%=build_dirs.python%>/site-packages/ni/'
                        : 'functional/ni/**',

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
                    'source/*.js'
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
                        'web/css/main_layout.scss',
                        'web/css/navigation.scss'
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
                'console': true,
                'angular': true
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
    grunt.registerTask('default', 'lint copy jsmin-sourcemap sass');
    grunt.registerTask('deploy', 'lint copy jsmin-sourcemap sass compress');
};