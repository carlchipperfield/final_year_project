function ContentFormatter () {

    return {

        /*
         *  Formats Session Description Language (SDP) content.
         *  Spec available at http://tools.ietf.org/pdf/rfc4566.pdf
         *
         *  @param content - raw sdp content
         *  returns an array of type-value sdp entries grouped
         */
        formatSDP: function (content) {

            var lines = content.trim().split('\n');

            // Extract each SDP type-value description
            var descriptions = [];
            for (var i = 0; i < lines.length; i++) {
                var line = lines[i].trim();
                if (line[1] === '=') {
                    descriptions.push({
                        type: line[0],
                        value: line.slice(2)
                    });
                }
            }

            // Group into different SDP sections
            i = 0;
            var session_description = [], media_descriptions = [];

            // First we need to group the session description
            while (i < descriptions.length && descriptions[i].type !== 'm') {
                session_description.push(descriptions[i]);
                i++;
            }

            // Then we need to group 0 or more media-level descriptions
            while (i < descriptions.length) {

                // Push the first media session line m=...
                var media_description = [descriptions[i]];
                i++;

                while (i < descriptions.length && descriptions[i].type !=='m') {
                    media_description.push(descriptions[i]);
                    i++;
                }
                media_descriptions.push(media_description);
            }

            return {
                'raw_content': content,
                'session_description': session_description,
                'media_descriptions':  media_descriptions
            };
        },

        /*
         *  Parse XML content.
         *
         *  @param content - xml string
         *  returns an array of xml elements
         */
        formatXML: function (content) {

            function extractXML (node) {

                var $node = $(node)[0];
                var child_nodes = $(node).children();
                var new_node = {};

                new_node['tag'] = $node.tagName;

                new_node['attributes'] = '';
                jQuery.each($node.attributes, function(){
                    new_node['attributes'] += ' ' + this.name + '="' + this.value + '"';
                });


                if ( child_nodes.length === 0 ) {
                    new_node['text'] = $node.textContent;
                    return new_node;
                }

                new_node['childNodes'] = [];
                child_nodes.each(function() {
                    new_node['childNodes'].push(extractXML(this));
                });

                return new_node;
            }

            content = content.trim();
            content = content.replace(/\n/g, '');
            content = content.replace(/ +/g, ' ');
            content = content.replace(/>\s+</g, '><');

            try {
                var parsed_content = jQuery.parseXML(content);

                return {
                    'version': parsed_content.xmlVersion,
                    'encoding': parsed_content.xmlEncoding,
                    'content': extractXML($(parsed_content).children())
                };
            }
            catch(e) {
                return {
                    'raw_content': content
                };
            }
        }
    };
}