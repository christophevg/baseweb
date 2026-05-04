/**
 * VuetifyFormGenerator - A Vue 3 + Vuetify 3 compatible form generator
 *
 * This component provides backward compatibility with vue-form-generator schemas
 * while using Vuetify 3 components for rendering.
 *
 * Supported field types:
 * - input / text -> v-text-field
 * - textarea -> v-textarea
 * - select -> v-select
 * - checkbox -> v-checkbox
 * - radio -> v-radio-group with v-radio children
 * - password -> v-text-field type="password"
 * - number -> v-text-field type="number"
 * - email -> v-text-field type="email"
 * - date -> v-text-field type="date"
 * - url -> v-text-field type="url"
 * - tel -> v-text-field type="tel"
 * - switch -> v-switch
 * - range -> v-slider
 * - color -> v-text-field type="color"
 *
 * Supported schema properties:
 * - label: field label
 * - model: model property path (supports nested paths like "address.city")
 * - type: field type
 * - inputType: alternative type specification for input fields
 * - placeholder: placeholder text
 * - hint: hint text shown below field
 * - required: marks field as required
 * - validator: custom validation function returning true or error message
 * - values: options for select/radio (array or function returning array)
 * - default: default value
 * - disabled: disabled state
 * - readonly: readonly state
 * - min: minimum value (for number/date/range)
 * - max: maximum value (for number/date/range)
 * - step: step value (for number/range)
 * - maxlength: maximum character length
 * - counter: show character counter
 * - clearable: show clear button
 * - prependIcon: icon before field
 * - appendIcon: icon after field
 * - rows: rows for textarea
 * - autoGrow: auto-grow textarea
 * - multiple: multiple selection for select
 * - visible: visibility (boolean or function)
 *
 * Schema format:
 * {
 *   fields: [
 *     { type: 'input', inputType: 'text', label: 'Name', model: 'name', required: true },
 *     { type: 'select', label: 'Category', model: 'category', values: ['A', 'B', 'C'] }
 *   ],
 *   groups: [  // optional field groups for layout
 *     { legend: 'Personal Info', fields: ['name', 'email'] }
 *   ]
 * }
 */

app.component("vue-form-generator", {
  name: "VuetifyFormGenerator",
  props: {
    schema: {
      type: Object,
      required: true,
      default: function() { return { fields: [] }; }
    },
    model: {
      type: Object,
      required: true,
      default: function() { return {}; }
    },
    options: {
      type: Object,
      default: function() { return {}; }
    }
  },
  data: function() {
    return {
      errors: {},      // validation errors per field
      touched: {}      // track touched fields for validation display
    };
  },
  computed: {
    // Get fields from schema, handling both direct fields and grouped fields
    allFields: function() {
      var self = this;
      var fields = [];

      if (self.schema.fields) {
        fields = fields.concat(self.schema.fields);
      }

      if (self.schema.groups) {
        self.schema.groups.forEach(function(group) {
          if (group.fields) {
            // Groups can reference fields by model name or contain field definitions
            group.fields.forEach(function(field) {
              if (typeof field === 'string') {
                // Find field definition by model name
                var found = self.schema.fields && self.schema.fields.find(function(f) {
                  return f.model === field;
                });
                if (found) {
                  fields.push(Object.assign({}, found, { group: group.legend }));
                }
              } else {
                field.group = group.legend;
                fields.push(field);
              }
            });
          }
        });
      }

      return fields;
    },

    // Group fields by their group property for rendering
    groupedFields: function() {
      var groups = { '': [] };
      this.allFields.forEach(function(field) {
        var groupName = field.group || '';
        if (!groups[groupName]) {
          groups[groupName] = [];
        }
        groups[groupName].push(field);
      });
      return groups;
    }
  },
  created: function() {
    // Apply default values when component is created
    this.applyDefaults();
  },
  methods: {
    // Get a value from the model using dot notation path
    getModelValue: function(path) {
      if (!path) return undefined;
      var parts = path.split('.');
      var value = this.model;
      for (var i = 0; i < parts.length; i++) {
        if (value === null || value === undefined) return undefined;
        value = value[parts[i]];
      }
      return value;
    },

    // Set a value in the model using dot notation path
    setModelValue: function(path, value) {
      if (!path) return;
      var parts = path.split('.');
      var obj = this.model;
      for (var i = 0; i < parts.length - 1; i++) {
        if (!obj[parts[i]]) {
          obj[parts[i]] = {};
        }
        obj = obj[parts[i]];
      }
      obj[parts[parts.length - 1]] = value;
      this.$emit('model-updated', this.model, path);
    },

    // Validate a single field
    validateField: function(field, value) {
      var self = this;

      // Required validation
      if (field.required) {
        if (value === undefined || value === null || value === '') {
          return field.requiredMessage || (field.label || field.model) + ' is required';
        }
      }

      // Custom validator
      if (field.validator && typeof field.validator === 'function') {
        var result = field.validator.call(self, value, field, self.model);
        if (result !== true && result !== undefined && result !== null) {
          return result;
        }
      }

      // Min/Max validation for numbers
      if (field.type === 'number' || field.inputType === 'number') {
        var numValue = parseFloat(value);
        if (!isNaN(numValue)) {
          if (field.min !== undefined && numValue < field.min) {
            return 'Minimum value is ' + field.min;
          }
          if (field.max !== undefined && numValue > field.max) {
            return 'Maximum value is ' + field.max;
          }
        }
      }

      // Maxlength validation
      if (field.maxlength && value && value.length > field.maxlength) {
        return 'Maximum length is ' + field.maxlength + ' characters';
      }

      // Email validation
      if ((field.type === 'email' || field.inputType === 'email') && value) {
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          return 'Please enter a valid email address';
        }
      }

      return null;
    },

    // Validate all fields and update errors
    validate: function() {
      var self = this;
      var valid = true;
      self.allFields.forEach(function(field) {
        var error = self.validateField(field, self.getModelValue(field.model));
        if (error) {
          self.errors[field.model] = error;
          valid = false;
        } else {
          self.errors[field.model] = null;
        }
      });
      return valid;
    },

    // Handle field input/change
    onFieldChange: function(field, value) {
      var self = this;
      self.setModelValue(field.model, value);
      self.touched[field.model] = true;

      // Validate on change if field has been touched
      if (self.touched[field.model]) {
        var error = self.validateField(field, value);
        self.errors[field.model] = error;
      }

      // Emit field-changed event
      self.$emit('field-changed', {
        field: field,
        value: value,
        model: self.model
      });
    },

    // Handle field blur for validation
    onFieldBlur: function(field) {
      var self = this;
      self.touched[field.model] = true;
      var value = self.getModelValue(field.model);
      var error = self.validateField(field, value);
      self.errors[field.model] = error;

      // Emit validated event
      self.$emit('validated', {
        field: field,
        value: value,
        error: error,
        model: self.model
      });
    },

    // Get field options for select/radio
    getFieldOptions: function(field) {
      if (field.values) {
        if (typeof field.values === 'function') {
          return field.values.call(this, this.model, field);
        }
        if (Array.isArray(field.values)) {
          // Handle array of strings or objects with name/value
          return field.values.map(function(item) {
            if (typeof item === 'object' && item !== null) {
              return {
                title: item.name || item.label || item.text || item.value,
                value: item.value !== undefined ? item.value : item
              };
            }
            return { title: String(item), value: item };
          });
        }
      }
      return [];
    },

    // Resolve field type to internal type
    getFieldType: function(field) {
      var type = field.type || 'input';
      var inputType = field.inputType;

      // Map vue-form-generator types
      var typeMap = {
        'input': 'text',
        'text': 'text',
        'textarea': 'textarea',
        'select': 'select',
        'checkbox': 'checkbox',
        'radio': 'radio',
        'password': 'password',
        'number': 'number',
        'email': 'email',
        'date': 'date',
        'url': 'url',
        'tel': 'tel',
        'range': 'range',
        'color': 'color',
        'switch': 'switch'
      };

      // Input type overrides if specified
      if (inputType && typeMap[inputType]) {
        return typeMap[inputType];
      }

      return typeMap[type] || 'text';
    },

    // Get the Vuetify component name for a field
    getFieldComponent: function(field) {
      var type = this.getFieldType(field);

      var componentMap = {
        'text': 'v-text-field',
        'password': 'v-text-field',
        'number': 'v-text-field',
        'email': 'v-text-field',
        'date': 'v-text-field',
        'url': 'v-text-field',
        'tel': 'v-text-field',
        'range': 'v-slider',
        'color': 'v-text-field',
        'textarea': 'v-textarea',
        'select': 'v-select',
        'checkbox': 'v-checkbox',
        'switch': 'v-switch',
        'radio': 'v-radio-group'
      };

      return componentMap[type] || 'v-text-field';
    },

    // Get props for the Vuetify component
    getFieldProps: function(field) {
      var self = this;
      var type = self.getFieldType(field);
      var value = self.getModelValue(field.model);

      var props = {
        modelValue: value,
        label: field.label,
        disabled: self.isFieldDisabled(field),
        readonly: self.isFieldReadonly(field),
        hint: field.hint,
        'persistent-hint': !!field.hint,
        id: self.getFieldId(field)
      };

      // Error handling
      if (self.errors[field.model]) {
        props.error = true;
        props['error-messages'] = [self.errors[field.model]];
      }

      // Add placeholder
      if (field.placeholder) {
        props.placeholder = field.placeholder;
      }

      // Add clearable
      if (field.clearable) {
        props.clearable = true;
      }

      // Add counter for text fields
      if (field.counter || field.maxlength) {
        props.counter = field.maxlength || true;
      }

      // Add icons
      if (field.prependIcon) {
        props['prepend-inner-icon'] = field.prependIcon;
      }
      if (field.appendIcon) {
        props['append-icon'] = field.appendIcon;
      }

      // Type-specific props
      switch (type) {
        case 'text':
        case 'password':
        case 'number':
        case 'email':
        case 'date':
        case 'url':
        case 'tel':
          props.type = type;
          if (field.maxlength) {
            props.maxlength = field.maxlength;
          }
          break;

        case 'textarea':
          props.type = 'text';
          if (field.rows) {
            props.rows = field.rows;
          }
          if (field.autoGrow) {
            props['auto-grow'] = true;
          }
          break;

        case 'select':
          props.items = self.getFieldOptions(field);
          props['item-title'] = 'title';
          props['item-value'] = 'value';
          if (field.multiple) {
            props.multiple = true;
            props.chips = true;
          }
          break;

        case 'checkbox':
        case 'switch':
          props.color = field.color || 'primary';
          break;

        case 'radio':
          // Radio group - color goes here too
          props.color = field.color || 'primary';
          break;

        case 'range':
          props.min = field.min || 0;
          props.max = field.max || 100;
          props.step = field.step || 1;
          props['thumb-label'] = true;
          break;

        case 'color':
          props.type = 'color';
          break;
      }

      // Number specific props
      if (type === 'number') {
        if (field.min !== undefined) props.min = field.min;
        if (field.max !== undefined) props.max = field.max;
        if (field.step !== undefined) props.step = field.step;
      }

      // Apply any additional attrs from field definition
      if (field.attrs) {
        Object.keys(field.attrs).forEach(function(key) {
          props[key] = field.attrs[key];
        });
      }

      // Apply style classes
      if (field.styleClasses) {
        props.class = field.styleClasses;
      } else {
        props.class = 'mb-3';
      }

      return props;
    },

    // Generate unique ID for field
    getFieldId: function(field) {
      return 'vfg-' + field.model.replace(/\./g, '-');
    },

    // Check if field is visible (supports visible property)
    isFieldVisible: function(field) {
      if (field.visible === undefined) return true;
      if (typeof field.visible === 'function') {
        return field.visible.call(this, this.model, field);
      }
      return field.visible;
    },

    // Check if field is disabled
    isFieldDisabled: function(field) {
      if (field.disabled === undefined) return false;
      if (typeof field.disabled === 'function') {
        return field.disabled.call(this, this.model, field);
      }
      return field.disabled;
    },

    // Check if field is readonly
    isFieldReadonly: function(field) {
      if (field.readonly === undefined) return false;
      if (typeof field.readonly === 'function') {
        return field.readonly.call(this, this.model, field);
      }
      return field.readonly;
    },

    // Apply default values to model
    applyDefaults: function() {
      var self = this;
      self.allFields.forEach(function(field) {
        var currentValue = self.getModelValue(field.model);
        if (currentValue === undefined && field.default !== undefined) {
          var defaultValue = typeof field.default === 'function'
            ? field.default.call(self, self.model, field)
            : field.default;
          self.setModelValue(field.model, defaultValue);
        }
      });
    }
  },
  template: `
<div class="vuetify-form-generator">
  <template v-for="(fields, groupName) in groupedFields">
    <fieldset v-if="groupName" class="vfg-group mb-4">
      <legend class="text-subtitle-1 font-weight-medium mb-2">${'{{'} groupName ${'}}'}</legend>
      <template v-for="field in fields">
        <template v-if="isFieldVisible(field)">
          <template v-if="getFieldType(field) === 'radio'">
            <v-radio-group
              :key="field.model"
              v-bind="getFieldProps(field)"
              @update:modelValue="onFieldChange(field, $event)"
            >
              <v-radio
                v-for="option in getFieldOptions(field)"
                :key="option.value"
                :label="option.title"
                :value="option.value"
              ></v-radio>
            </v-radio-group>
          </template>
          <template v-else>
            <component
              :is="getFieldComponent(field)"
              :key="field.model"
              v-bind="getFieldProps(field)"
              @update:modelValue="onFieldChange(field, $event)"
              @blur="onFieldBlur(field)"
            ></component>
          </template>
        </template>
      </template>
    </fieldset>
    <template v-else>
      <template v-for="field in fields">
        <template v-if="isFieldVisible(field)">
          <template v-if="getFieldType(field) === 'radio'">
            <v-radio-group
              :key="field.model"
              v-bind="getFieldProps(field)"
              @update:modelValue="onFieldChange(field, $event)"
            >
              <v-radio
                v-for="option in getFieldOptions(field)"
                :key="option.value"
                :label="option.title"
                :value="option.value"
              ></v-radio>
            </v-radio-group>
          </template>
          <template v-else>
            <component
              :is="getFieldComponent(field)"
              :key="field.model"
              v-bind="getFieldProps(field)"
              @update:modelValue="onFieldChange(field, $event)"
              @blur="onFieldBlur(field)"
            ></component>
          </template>
        </template>
      </template>
    </template>
  </template>
</div>
`
});