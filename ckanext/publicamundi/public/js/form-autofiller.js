
this.ckan.module('form-autofiller', function ($, _) {
    
  return {
    
    samples: {
        "resource-form": [
            {
                'url': 'http://example.com/res/1',
                'description': 'A very interesting example',
                'name': 'A web page example',
                'format': 'html',
            },
            {
                'url': window.location.origin + '/samples/1.csv',
                'description': 'A quite interesting example',
                'name': 'A CSV example',
                'format': 'csv',
            },
        ],
        "package-form": [
            {
                'title': 'Hello Foo 1',
                'name': 'hello-foo-1',
                'dataset_type': 'foo',
                'notes': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do ' +
                         'eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                'tags': ['hello-world', 'foo', 'lorem-ipsum'],
                'license': 'gfdl',
                'version': '1.0.1',
                'author': 'Λαλάκης',
                'author_email': 'lalakis@example.com',
            },
            {
                'title': 'Hello Foo 2',
                'name': 'hello-foo-2',
                'dataset_type': 'foo',
                'notes': 'I am another _Foo_ package!',
                'tags': ['hello-world', 'foo', 'test'],
                'license': 'cc-by',
                'version': '1.0.2',
                'author': 'Φουφουτος',
                'author_email': 'foofootos@example.com',
            },    

        ],
    },
    
    _sample: function(formid) 
    {
        var samples = this.samples[formid]
        var i = Math.floor(Math.random() * 1e4) % samples.length
        return samples[i]
    },
    
    options: {
        formid: 'package-form',
    },

    initialize: function() 
    {
        var module = this
        var el = this.el

        var $form = $('#' + this.options.formid)

        switch (this.options.formid) {
            default:
            case 'package-form':
                {
                    this.el.on('click', function() {
                        data = module._sample(module.options.formid)
                        $form.find('#field-title').val(data['title'])
                        $form.find('#field-name').val(data['name'])
                        $form.find('#field-dataset_type').select2('val', data['dataset_type'])
                        $form.find('#field-notes').val(data['notes'])
                        $form.find('#field-tags').select2('val', data['tags'])
                        $form.find('#field-license').select2('val', data['license'])
                        $form.find('#field-version').val(data['license'])
                        $form.find('#field-author').val(data['author'])
                        $form.find('#field-author_email').val(data['author_email'])
                    })
                    this.el.css('margin', '0px 5px')
                    this.el.insertBefore($form.find('button.btn-primary[name="save"]').first())
                    this.el.show()
                }
                break;
            case 'resource-form':
                {
                    this.el.on('click', function() {
                        data = module._sample(module.options.formid)
                        $form.find("label[for='field-image-upload']").parent().find('.btn:visible:eq(1)').click()
                        $form.find('#field-image-url').val(data['url'])
                        $form.find('#field-name').val(data['name'])
                        $form.find('#field-description').val(data['description'])
                        $form.find('#field-format').select2('val', data['format'])
                    })
                    this.el.css('margin', '0px 5px')
                    this.el.insertBefore($form.find('button.btn-primary[name="save"]').first())
                    this.el.show()
                }
                break;
        }

        window.console.log('Initialized module: form-autofiller')
    },
    teardown: function() { 
        window.console.log('Tearing down module: form-autofiller')
    },
  }
})
