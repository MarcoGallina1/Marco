odoo.define('toperp_theme.SaasLimit', function (require) {

    const Pager = require('web.Pager');
    const ListView = require('web.ListView');
    const KanbanView = require('web.KanbanView');

    const PAGER_LEVEL = ['1-10', '1-30', '1-50', '1-100'];

    Pager.include({
        _edit: function () {
            if (this.options.can_edit) {
                var self = this;
                // var $input = $('<input>', {class: 'o_input', type: 'text', value: this.$value.html()});
                const $input = $('<select>', {class: 'o_input'});
                _.each(PAGER_LEVEL, function (level) {
                    const $option = $('<option>', {value: level}).html(level);
                    $input.append($option);
                });
                $input.val(this.$value.html());

                this.$value.html($input);
                $input.focus();

                // Event handlers
                $input.click(function (ev) {
                    ev.stopPropagation(); // ignore clicks on the input
                });
                $input.blur(function (ev) {
                    self._render(); // save the state when leaving the input
                });
                $input.change(function (ev) {
                    self._save($(ev.target)); // save the state when leaving the input
                });
                $input.on('keydown', function (ev) {
                    ev.stopPropagation();
                    if (ev.which === $.ui.keyCode.ENTER) {
                        self._save($(ev.target)); // save on enter
                    } else if (ev.which === $.ui.keyCode.ESCAPE) {
                        self._render(); // leave on escape
                    }
                });
            }
        },
    });

    KanbanView.include({
        init: function () {
            this._super.apply(this, arguments);
            this.loadParams.limit = this.loadParams.limit && this.loadParams.limit <= 24 || 24;
        }
    });

    ListView.include({
        init: function () {
            this._super.apply(this, arguments);
            this.loadParams.limit = this.loadParams.limit && this.loadParams.limit <= 30 || 30;
            this.loadParams.groupsLimit = this.loadParams.groupsLimit && this.loadParams.groupsLimit <= 10 || 10;
        }
    })

});