from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from clarusui.gridvisualisationelement import GridViz
from clarusui.layout import Element

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(
    loader=FileSystemLoader(THIS_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

tableTemplate = env.get_template('table.html')

class Table(GridViz):
    def __init__(self, response, **options):
        super(self.__class__, self).__init__(response,**options)
        self._dataFrame.insert(0, self._dataFrame.index[0] if self._dataFrame.index.name is None else self._dataFrame.index.name, self._dataFrame.index) #add a column with values from index at beginning as we want to display these too
        self.defaultDisplayFormat = options.pop('defaultDisplayFormat', '{:,.0f}')
        self.columnDisplayFormats = options.pop('columnDisplayFormats', None)
        self.columnColourLogic = options.pop('columnColourLogic', None)
        self._set_headers(self._get_filtered_col_headers())
        self._set_rows()    
        self.set_header_css_class(options.pop('headerCssClass', None))
        self.set_header_colour(options.pop('headerColour', None))
        
        
    def set_header_css_class(self, headerCssClass):        
        if (headerCssClass is not None):
            for header in self.headers:
                header.set_css_class(headerCssClass)
                
    def set_header_colour(self, colour):
        if colour is not None:
            for header in self.headers:
                header.set_bgcolour(colour)
    
    def set_column_header_colour(self, column, colour):
        header = self.headers[column]
        header.set_bgcolour(colour)
                
    def get_column_display_format(self, columnName):
        displayFormat = None
        if self.columnDisplayFormats is not None:
            displayFormat = self.columnDisplayFormats.get(columnName)
        
        if displayFormat is not None:
            return displayFormat
        else:
            return self.defaultDisplayFormat
        
    def _get_column_colour_logic(self, columnName):
        if self.columnColourLogic is not None:
            return self.columnColourLogic.get(columnName)
        return None
    
    def _eval_column_colour_logic(self, columnName, cellValue):
        logic = self._get_column_colour_logic(columnName)
        if logic is not None:
            return logic(cellValue)
        return None
        
               
    def _set_headers(self, headers):
        self.headers = []
       
        for header in headers:
            headerCell = Cell(header)
            self.headers.append(headerCell)
    
    def _set_rows(self):
        self.rows = []
        rowIdx = 0
        for row in self._get_filtered_row_headers():
            r = []
            colIdx = 0
            for header in self.headers:
                cell = Cell(self._get_value(row if self._dataFrame.index.is_unique else rowIdx, header.cellvalue if self._dataFrame.index.is_unique else colIdx), numberFormat=self.get_column_display_format(header.cellvalue))
                colour = self._eval_column_colour_logic(header.get_cell_value(), cell.get_cell_value())
                if colour is not None:
                    cell.set_bgcolour(colour)
                r.append(cell)
                if cell._is_numeric(): #right align number cells
                    header.add_custom_css({'text-align':'right'})
                colIdx += 1
            self.rows.append(r)
            rowIdx += 1
    
    
    def get_cell(self, row, column):
        return self.rows[row][column]
    
    def _render(self):
        return tableTemplate.render(table=self)
    
    def toDiv(self):
        return self._render()
    
    #will set a flag against any cell with country name match - allow per column/cell etc?
    def add_country_flags(self):
        for row in self.rows:
            for cell in row:
                cv = cell.get_cell_value()
                countryCode = get_country_code(cv)
                if countryCode is not None:
                    cell.set_icon('flag-icon flag-icon-'+countryCode.lower())
                    
        
    
        
class Cell(Element):
    def __init__(self, cellvalue, **options):
        super(self.__class__, self).__init__(None,**options)
        self.numberFormat = options.pop('numberFormat', '{:,.0f}')
        self.cellvalue = cellvalue
        self.iconName = None
        self.iconAlignment = 'left'
        if self._is_numeric():
            self.add_custom_css({'text-align':'right'})
    
    def _is_numeric(self):
        if self.cellvalue is None:
            return False
        try:
            x = float(self.cellvalue)
            return True
        except Exception:
            return False
    
    def set_number_format(self, numberFormat):
        self.numberFormat = numberFormat;
    
    def set_icon(self, iconName, iconAlignment='left'):
        self.iconName = iconName
        self.iconAlignment = iconAlignment
    
    def _iconify_cell(self, cellValue):
        if self.iconName is None:
            return cellValue
        iconCode = '<i class="'+self.iconName+'" aria-hidden="true"></i>'
        if self.iconAlignment == 'left':
            cellValue = iconCode + ' ' +cellValue
        else: 
            cellValue = cellValue + ' ' +iconCode
        return cellValue
            
    
    def get_cell_value(self):
        cv = ''
        if self._is_numeric():
            cv = self.numberFormat.format(float(self.cellvalue))
        else:
            cv = self.cellvalue
        
        return self._iconify_cell(cv)
            
    def toDiv(self):
        raise NotImplementedError("Table cell not suitable for standalone usage")

#should really be somewhere else as a utility method
def get_country_code(countryName):
    dict = {"Aruba":"AW",
"Afghanistan":"AF",
"Angola":"AO",
"Anguilla":"AI",
"Albania":"AL",
"Andorra":"AD",
"United Arab Emirates":"AE",
"Argentina":"AR",
"Armenia":"AM",
"American Samoa":"AS",
"Antarctica":"AQ",
"French Southern Territories":"TF",
"Antigua and Barbuda":"AG",
"Australia":"AU",
"Austria":"AT",
"Azerbaijan":"AZ",
"Burundi":"BI",
"Belgium":"BE",
"Benin":"BJ",
"Bonaire, Sint Eustatius and Saba":"BQ",
"Burkina Faso":"BF",
"Bangladesh":"BD",
"Bulgaria":"BG",
"Bahrain":"BH",
"Bahamas":"BS",
"Bosnia and Herzegovina":"BA",
"Belarus":"BY",
"Belize":"BZ",
"Bermuda":"BM",
"Bolivia, Plurinational State of":"BO",
"Brazil":"BR",
"Barbados":"BB",
"Brunei Darussalam":"BN",
"Bhutan":"BT",
"Bouvet Island":"BV",
"Botswana":"BW",
"Central African Republic":"CF",
"Canada":"CA",
"Cocos (Keeling) Islands":"CC",
"Switzerland":"CH",
"Chile":"CL",
"China":"CN",
"Cameroon":"CM",
"Congo, The Democratic Republic of the":"CD",
"Congo":"CG",
"Cook Islands":"CK",
"Colombia":"CO",
"Comoros":"KM",
"Cabo Verde":"CV",
"Costa Rica":"CR",
"Cuba":"CU",
"Christmas Island":"CX",
"Cayman Islands":"KY",
"Cyprus":"CY",
"Czechia":"CZ",
"Germany":"DE",
"Djibouti":"DJ",
"Dominica":"DM",
"Denmark":"DK",
"Dominican Republic":"DO",
"Algeria":"DZ",
"Ecuador":"EC",
"Egypt":"EG",
"Eritrea":"ER",
"Western Sahara":"EH",
"Spain":"ES",
"Estonia":"EE",
"Ethiopia":"ET",
"Finland":"FI",
"Fiji":"FJ",
"Falkland Islands (Malvinas)":"FK",
"France":"FR",
"Faroe Islands":"FO",
"Micronesia, Federated States of":"FM",
"Gabon":"GA",
"United Kingdom":"GB",
"Georgia":"GE",
"Guernsey":"GG",
"Ghana":"GH",
"Gibraltar":"GI",
"Guinea":"GN",
"Guadeloupe":"GP",
"Gambia":"GM",
"Guinea-Bissau":"GW",
"Equatorial Guinea":"GQ",
"Greece":"GR",
"Grenada":"GD",
"Greenland":"GL",
"Guatemala":"GT",
"French Guiana":"GF",
"Guam":"GU",
"Guyana":"GY",
"Hong Kong":"HK",
"Heard Island and McDonald Islands":"HM",
"Honduras":"HN",
"Croatia":"HR",
"Haiti":"HT",
"Hungary":"HU",
"Indonesia":"ID",
"Isle of Man":"IM",
"India":"IN",
"British Indian Ocean Territory":"IO",
"Ireland":"IE",
"Iran, Islamic Republic of":"IR",
"Iraq":"IQ",
"Iceland":"IS",
"Israel":"IL",
"Italy":"IT",
"Jamaica":"JM",
"Jersey":"JE",
"Jordan":"JO",
"Japan":"JP",
"Kazakhstan":"KZ",
"Kenya":"KE",
"Kyrgyzstan":"KG",
"Cambodia":"KH",
"Kiribati":"KI",
"Saint Kitts and Nevis":"KN",
"Korea, Republic of":"KR",
"Kuwait":"KW",
"Lao People's Democratic Republic":"LA",
"Lebanon":"LB",
"Liberia":"LR",
"Libya":"LY",
"Saint Lucia":"LC",
"Liechtenstein":"LI",
"Sri Lanka":"LK",
"Lesotho":"LS",
"Lithuania":"LT",
"Luxembourg":"LU",
"Latvia":"LV",
"Macao":"MO",
"Saint Martin (French part)":"MF",
"Morocco":"MA",
"Monaco":"MC",
"Moldova, Republic of":"MD",
"Madagascar":"MG",
"Maldives":"MV",
"Mexico":"MX",
"Marshall Islands":"MH",
"Macedonia, Republic of":"MK",
"Mali":"ML",
"Malta":"MT",
"Myanmar":"MM",
"Montenegro":"ME",
"Mongolia":"MN",
"Northern Mariana Islands":"MP",
"Mozambique":"MZ",
"Mauritania":"MR",
"Montserrat":"MS",
"Martinique":"MQ",
"Mauritius":"MU",
"Malawi":"MW",
"Malaysia":"MY",
"Mayotte":"YT",
"Namibia":"NA",
"New Caledonia":"NC",
"Niger":"NE",
"Norfolk Island":"NF",
"Nigeria":"NG",
"Nicaragua":"NI",
"Niue":"NU",
"Netherlands":"NL",
"Norway":"NO",
"Nepal":"NP",
"Nauru":"NR",
"New Zealand":"NZ",
"Oman":"OM",
"Pakistan":"PK",
"Panama":"PA",
"Pitcairn":"PN",
"Peru":"PE",
"Philippines":"PH",
"Palau":"PW",
"Papua New Guinea":"PG",
"Poland":"PL",
"Puerto Rico":"PR",
"Korea, Democratic People's Republic of":"KP",
"Portugal":"PT",
"Paraguay":"PY",
"Palestine, State of":"PS",
"French Polynesia":"PF",
"Qatar":"QA",
"Romania":"RO",
"Russian Federation":"RU",
"Rwanda":"RW",
"Saudi Arabia":"SA",
"Sudan":"SD",
"Senegal":"SN",
"Singapore":"SG",
"South Georgia and the South Sandwich Islands":"GS",
"Saint Helena, Ascension and Tristan da Cunha":"SH",
"Svalbard and Jan Mayen":"SJ",
"Solomon Islands":"SB",
"Sierra Leone":"SL",
"El Salvador":"SV",
"San Marino":"SM",
"Somalia":"SO",
"Saint Pierre and Miquelon":"PM",
"Serbia":"RS",
"South Sudan":"SS",
"Sao Tome and Principe":"ST",
"Suriname":"SR",
"Slovakia":"SK",
"Slovenia":"SI",
"Sweden":"SE",
"Swaziland":"SZ",
"Sint Maarten (Dutch part)":"SX",
"Seychelles":"SC",
"Syrian Arab Republic":"SY",
"Turks and Caicos Islands":"TC",
"Chad":"TD",
"Togo":"TG",
"Thailand":"TH",
"Tajikistan":"TJ",
"Tokelau":"TK",
"Turkmenistan":"TM",
"Timor-Leste":"TL",
"Tonga":"TO",
"Trinidad and Tobago":"TT",
"Tunisia":"TN",
"Turkey":"TR",
"Tuvalu":"TV",
"Taiwan, Province of China":"TW",
"Tanzania, United Republic of":"TZ",
"Uganda":"UG",
"Ukraine":"UA",
"United States Minor Outlying Islands":"UM",
"Uruguay":"UY",
"United States":"US",
"Uzbekistan":"UZ",
"Holy See (Vatican City State)":"VA",
"Saint Vincent and the Grenadines":"VC",
"Venezuela, Bolivarian Republic of":"VE",
"Virgin Islands, British":"VG",
"Virgin Islands, U.S.":"VI",
"Viet Nam":"VN",
"Vanuatu":"VU",
"Wallis and Futuna":"WF",
"Samoa":"WS",
"Yemen":"YE",
"South Africa":"ZA",
"Zambia":"ZM",
"Zimbabwe":"ZW"}
    return dict.get(countryName)