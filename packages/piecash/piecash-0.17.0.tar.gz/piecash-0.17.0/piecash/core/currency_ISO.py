# coding=utf-8
from collections import namedtuple
from xml.etree import ElementTree

ISO_type = namedtuple("ISO_type", "country	currency	mnemonic	cusip	fraction".split("\t"))

# https://www.currency-iso.org/dam/downloads/lists/list_one.xml
ISO_currencies_XML = """<ISO_4217 Pblshd="2017-01-01">
<CcyTbl>
<CcyNtry>
<CtryNm>AFGHANISTAN</CtryNm>
<CcyNm>Afghani</CcyNm>
<Ccy>AFN</Ccy>
<CcyNbr>971</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ÅLAND ISLANDS</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ALBANIA</CtryNm>
<CcyNm>Lek</CcyNm>
<Ccy>ALL</Ccy>
<CcyNbr>008</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ALGERIA</CtryNm>
<CcyNm>Algerian Dinar</CcyNm>
<Ccy>DZD</Ccy>
<CcyNbr>012</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>AMERICAN SAMOA</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ANDORRA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ANGOLA</CtryNm>
<CcyNm>Kwanza</CcyNm>
<Ccy>AOA</Ccy>
<CcyNbr>973</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ANGUILLA</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ANTARCTICA</CtryNm>
<CcyNm>No universal currency</CcyNm>
</CcyNtry>
<CcyNtry>
<CtryNm>ANTIGUA AND BARBUDA</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ARGENTINA</CtryNm>
<CcyNm>Argentine Peso</CcyNm>
<Ccy>ARS</Ccy>
<CcyNbr>032</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ARMENIA</CtryNm>
<CcyNm>Armenian Dram</CcyNm>
<Ccy>AMD</Ccy>
<CcyNbr>051</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ARUBA</CtryNm>
<CcyNm>Aruban Florin</CcyNm>
<Ccy>AWG</Ccy>
<CcyNbr>533</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>AUSTRALIA</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>AUSTRIA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>AZERBAIJAN</CtryNm>
<CcyNm>Azerbaijanian Manat</CcyNm>
<Ccy>AZN</Ccy>
<CcyNbr>944</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BAHAMAS (THE)</CtryNm>
<CcyNm>Bahamian Dollar</CcyNm>
<Ccy>BSD</Ccy>
<CcyNbr>044</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BAHRAIN</CtryNm>
<CcyNm>Bahraini Dinar</CcyNm>
<Ccy>BHD</Ccy>
<CcyNbr>048</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BANGLADESH</CtryNm>
<CcyNm>Taka</CcyNm>
<Ccy>BDT</Ccy>
<CcyNbr>050</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BARBADOS</CtryNm>
<CcyNm>Barbados Dollar</CcyNm>
<Ccy>BBD</Ccy>
<CcyNbr>052</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BELARUS</CtryNm>
<CcyNm>Belarusian Ruble</CcyNm>
<Ccy>BYN</Ccy>
<CcyNbr>933</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BELGIUM</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BELIZE</CtryNm>
<CcyNm>Belize Dollar</CcyNm>
<Ccy>BZD</Ccy>
<CcyNbr>084</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BENIN</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BERMUDA</CtryNm>
<CcyNm>Bermudian Dollar</CcyNm>
<Ccy>BMD</Ccy>
<CcyNbr>060</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BHUTAN</CtryNm>
<CcyNm>Indian Rupee</CcyNm>
<Ccy>INR</Ccy>
<CcyNbr>356</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BHUTAN</CtryNm>
<CcyNm>Ngultrum</CcyNm>
<Ccy>BTN</Ccy>
<CcyNbr>064</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BOLIVIA (PLURINATIONAL STATE OF)</CtryNm>
<CcyNm>Boliviano</CcyNm>
<Ccy>BOB</Ccy>
<CcyNbr>068</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BOLIVIA (PLURINATIONAL STATE OF)</CtryNm>
<CcyNm IsFund="true">Mvdol</CcyNm>
<Ccy>BOV</Ccy>
<CcyNbr>984</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BONAIRE, SINT EUSTATIUS AND SABA</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BOSNIA AND HERZEGOVINA</CtryNm>
<CcyNm>Convertible Mark</CcyNm>
<Ccy>BAM</Ccy>
<CcyNbr>977</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BOTSWANA</CtryNm>
<CcyNm>Pula</CcyNm>
<Ccy>BWP</Ccy>
<CcyNbr>072</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BOUVET ISLAND</CtryNm>
<CcyNm>Norwegian Krone</CcyNm>
<Ccy>NOK</Ccy>
<CcyNbr>578</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BRAZIL</CtryNm>
<CcyNm>Brazilian Real</CcyNm>
<Ccy>BRL</Ccy>
<CcyNbr>986</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BRITISH INDIAN OCEAN TERRITORY (THE)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BRUNEI DARUSSALAM</CtryNm>
<CcyNm>Brunei Dollar</CcyNm>
<Ccy>BND</Ccy>
<CcyNbr>096</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BULGARIA</CtryNm>
<CcyNm>Bulgarian Lev</CcyNm>
<Ccy>BGN</Ccy>
<CcyNbr>975</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BURKINA FASO</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>BURUNDI</CtryNm>
<CcyNm>Burundi Franc</CcyNm>
<Ccy>BIF</Ccy>
<CcyNbr>108</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CABO VERDE</CtryNm>
<CcyNm>Cabo Verde Escudo</CcyNm>
<Ccy>CVE</Ccy>
<CcyNbr>132</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CAMBODIA</CtryNm>
<CcyNm>Riel</CcyNm>
<Ccy>KHR</Ccy>
<CcyNbr>116</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CAMEROON</CtryNm>
<CcyNm>CFA Franc BEAC</CcyNm>
<Ccy>XAF</Ccy>
<CcyNbr>950</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CANADA</CtryNm>
<CcyNm>Canadian Dollar</CcyNm>
<Ccy>CAD</Ccy>
<CcyNbr>124</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CAYMAN ISLANDS (THE)</CtryNm>
<CcyNm>Cayman Islands Dollar</CcyNm>
<Ccy>KYD</Ccy>
<CcyNbr>136</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CENTRAL AFRICAN REPUBLIC (THE)</CtryNm>
<CcyNm>CFA Franc BEAC</CcyNm>
<Ccy>XAF</Ccy>
<CcyNbr>950</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CHAD</CtryNm>
<CcyNm>CFA Franc BEAC</CcyNm>
<Ccy>XAF</Ccy>
<CcyNbr>950</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CHILE</CtryNm>
<CcyNm>Chilean Peso</CcyNm>
<Ccy>CLP</Ccy>
<CcyNbr>152</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CHILE</CtryNm>
<CcyNm IsFund="true">Unidad de Fomento</CcyNm>
<Ccy>CLF</Ccy>
<CcyNbr>990</CcyNbr>
<CcyMnrUnts>4</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CHINA</CtryNm>
<CcyNm>Yuan Renminbi</CcyNm>
<Ccy>CNY</Ccy>
<CcyNbr>156</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CHRISTMAS ISLAND</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>COCOS (KEELING) ISLANDS (THE)</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>COLOMBIA</CtryNm>
<CcyNm>Colombian Peso</CcyNm>
<Ccy>COP</Ccy>
<CcyNbr>170</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>COLOMBIA</CtryNm>
<CcyNm IsFund="true">Unidad de Valor Real</CcyNm>
<Ccy>COU</Ccy>
<CcyNbr>970</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>COMOROS (THE)</CtryNm>
<CcyNm>Comoro Franc</CcyNm>
<Ccy>KMF</Ccy>
<CcyNbr>174</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CONGO (THE DEMOCRATIC REPUBLIC OF THE)</CtryNm>
<CcyNm>Congolese Franc</CcyNm>
<Ccy>CDF</Ccy>
<CcyNbr>976</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CONGO (THE)</CtryNm>
<CcyNm>CFA Franc BEAC</CcyNm>
<Ccy>XAF</Ccy>
<CcyNbr>950</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>COOK ISLANDS (THE)</CtryNm>
<CcyNm>New Zealand Dollar</CcyNm>
<Ccy>NZD</Ccy>
<CcyNbr>554</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>COSTA RICA</CtryNm>
<CcyNm>Costa Rican Colon</CcyNm>
<Ccy>CRC</Ccy>
<CcyNbr>188</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CÔTE D'IVOIRE</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CROATIA</CtryNm>
<CcyNm>Kuna</CcyNm>
<Ccy>HRK</Ccy>
<CcyNbr>191</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CUBA</CtryNm>
<CcyNm>Cuban Peso</CcyNm>
<Ccy>CUP</Ccy>
<CcyNbr>192</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CUBA</CtryNm>
<CcyNm>Peso Convertible</CcyNm>
<Ccy>CUC</Ccy>
<CcyNbr>931</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CURAÇAO</CtryNm>
<CcyNm>Netherlands Antillean Guilder</CcyNm>
<Ccy>ANG</Ccy>
<CcyNbr>532</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CYPRUS</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>CZECH REPUBLIC (THE)</CtryNm>
<CcyNm>Czech Koruna</CcyNm>
<Ccy>CZK</Ccy>
<CcyNbr>203</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>DENMARK</CtryNm>
<CcyNm>Danish Krone</CcyNm>
<Ccy>DKK</Ccy>
<CcyNbr>208</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>DJIBOUTI</CtryNm>
<CcyNm>Djibouti Franc</CcyNm>
<Ccy>DJF</Ccy>
<CcyNbr>262</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>DOMINICA</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>DOMINICAN REPUBLIC (THE)</CtryNm>
<CcyNm>Dominican Peso</CcyNm>
<Ccy>DOP</Ccy>
<CcyNbr>214</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ECUADOR</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>EGYPT</CtryNm>
<CcyNm>Egyptian Pound</CcyNm>
<Ccy>EGP</Ccy>
<CcyNbr>818</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>EL SALVADOR</CtryNm>
<CcyNm>El Salvador Colon</CcyNm>
<Ccy>SVC</Ccy>
<CcyNbr>222</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>EL SALVADOR</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>EQUATORIAL GUINEA</CtryNm>
<CcyNm>CFA Franc BEAC</CcyNm>
<Ccy>XAF</Ccy>
<CcyNbr>950</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ERITREA</CtryNm>
<CcyNm>Nakfa</CcyNm>
<Ccy>ERN</Ccy>
<CcyNbr>232</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ESTONIA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ETHIOPIA</CtryNm>
<CcyNm>Ethiopian Birr</CcyNm>
<Ccy>ETB</Ccy>
<CcyNbr>230</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>EUROPEAN UNION</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FALKLAND ISLANDS (THE) [MALVINAS]</CtryNm>
<CcyNm>Falkland Islands Pound</CcyNm>
<Ccy>FKP</Ccy>
<CcyNbr>238</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FAROE ISLANDS (THE)</CtryNm>
<CcyNm>Danish Krone</CcyNm>
<Ccy>DKK</Ccy>
<CcyNbr>208</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FIJI</CtryNm>
<CcyNm>Fiji Dollar</CcyNm>
<Ccy>FJD</Ccy>
<CcyNbr>242</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FINLAND</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FRANCE</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FRENCH GUIANA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FRENCH POLYNESIA</CtryNm>
<CcyNm>CFP Franc</CcyNm>
<Ccy>XPF</Ccy>
<CcyNbr>953</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>FRENCH SOUTHERN TERRITORIES (THE)</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GABON</CtryNm>
<CcyNm>CFA Franc BEAC</CcyNm>
<Ccy>XAF</Ccy>
<CcyNbr>950</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GAMBIA (THE)</CtryNm>
<CcyNm>Dalasi</CcyNm>
<Ccy>GMD</Ccy>
<CcyNbr>270</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GEORGIA</CtryNm>
<CcyNm>Lari</CcyNm>
<Ccy>GEL</Ccy>
<CcyNbr>981</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GERMANY</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GHANA</CtryNm>
<CcyNm>Ghana Cedi</CcyNm>
<Ccy>GHS</Ccy>
<CcyNbr>936</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GIBRALTAR</CtryNm>
<CcyNm>Gibraltar Pound</CcyNm>
<Ccy>GIP</Ccy>
<CcyNbr>292</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GREECE</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GREENLAND</CtryNm>
<CcyNm>Danish Krone</CcyNm>
<Ccy>DKK</Ccy>
<CcyNbr>208</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GRENADA</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUADELOUPE</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUAM</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUATEMALA</CtryNm>
<CcyNm>Quetzal</CcyNm>
<Ccy>GTQ</Ccy>
<CcyNbr>320</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUERNSEY</CtryNm>
<CcyNm>Pound Sterling</CcyNm>
<Ccy>GBP</Ccy>
<CcyNbr>826</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUINEA</CtryNm>
<CcyNm>Guinea Franc</CcyNm>
<Ccy>GNF</Ccy>
<CcyNbr>324</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUINEA-BISSAU</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>GUYANA</CtryNm>
<CcyNm>Guyana Dollar</CcyNm>
<Ccy>GYD</Ccy>
<CcyNbr>328</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HAITI</CtryNm>
<CcyNm>Gourde</CcyNm>
<Ccy>HTG</Ccy>
<CcyNbr>332</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HAITI</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HEARD ISLAND AND McDONALD ISLANDS</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HOLY SEE (THE)</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HONDURAS</CtryNm>
<CcyNm>Lempira</CcyNm>
<Ccy>HNL</Ccy>
<CcyNbr>340</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HONG KONG</CtryNm>
<CcyNm>Hong Kong Dollar</CcyNm>
<Ccy>HKD</Ccy>
<CcyNbr>344</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>HUNGARY</CtryNm>
<CcyNm>Forint</CcyNm>
<Ccy>HUF</Ccy>
<CcyNbr>348</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ICELAND</CtryNm>
<CcyNm>Iceland Krona</CcyNm>
<Ccy>ISK</Ccy>
<CcyNbr>352</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>INDIA</CtryNm>
<CcyNm>Indian Rupee</CcyNm>
<Ccy>INR</Ccy>
<CcyNbr>356</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>INDONESIA</CtryNm>
<CcyNm>Rupiah</CcyNm>
<Ccy>IDR</Ccy>
<CcyNbr>360</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>INTERNATIONAL MONETARY FUND (IMF)</CtryNm>
<CcyNm>SDR (Special Drawing Right)</CcyNm>
<Ccy>XDR</Ccy>
<CcyNbr>960</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>IRAN (ISLAMIC REPUBLIC OF)</CtryNm>
<CcyNm>Iranian Rial</CcyNm>
<Ccy>IRR</Ccy>
<CcyNbr>364</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>IRAQ</CtryNm>
<CcyNm>Iraqi Dinar</CcyNm>
<Ccy>IQD</Ccy>
<CcyNbr>368</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>IRELAND</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ISLE OF MAN</CtryNm>
<CcyNm>Pound Sterling</CcyNm>
<Ccy>GBP</Ccy>
<CcyNbr>826</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ISRAEL</CtryNm>
<CcyNm>New Israeli Sheqel</CcyNm>
<Ccy>ILS</Ccy>
<CcyNbr>376</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ITALY</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>JAMAICA</CtryNm>
<CcyNm>Jamaican Dollar</CcyNm>
<Ccy>JMD</Ccy>
<CcyNbr>388</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>JAPAN</CtryNm>
<CcyNm>Yen</CcyNm>
<Ccy>JPY</Ccy>
<CcyNbr>392</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>JERSEY</CtryNm>
<CcyNm>Pound Sterling</CcyNm>
<Ccy>GBP</Ccy>
<CcyNbr>826</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>JORDAN</CtryNm>
<CcyNm>Jordanian Dinar</CcyNm>
<Ccy>JOD</Ccy>
<CcyNbr>400</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KAZAKHSTAN</CtryNm>
<CcyNm>Tenge</CcyNm>
<Ccy>KZT</Ccy>
<CcyNbr>398</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KENYA</CtryNm>
<CcyNm>Kenyan Shilling</CcyNm>
<Ccy>KES</Ccy>
<CcyNbr>404</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KIRIBATI</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KOREA (THE DEMOCRATIC PEOPLE’S REPUBLIC OF)</CtryNm>
<CcyNm>North Korean Won</CcyNm>
<Ccy>KPW</Ccy>
<CcyNbr>408</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KOREA (THE REPUBLIC OF)</CtryNm>
<CcyNm>Won</CcyNm>
<Ccy>KRW</Ccy>
<CcyNbr>410</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KUWAIT</CtryNm>
<CcyNm>Kuwaiti Dinar</CcyNm>
<Ccy>KWD</Ccy>
<CcyNbr>414</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>KYRGYZSTAN</CtryNm>
<CcyNm>Som</CcyNm>
<Ccy>KGS</Ccy>
<CcyNbr>417</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LAO PEOPLE’S DEMOCRATIC REPUBLIC (THE)</CtryNm>
<CcyNm>Kip</CcyNm>
<Ccy>LAK</Ccy>
<CcyNbr>418</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LATVIA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LEBANON</CtryNm>
<CcyNm>Lebanese Pound</CcyNm>
<Ccy>LBP</Ccy>
<CcyNbr>422</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LESOTHO</CtryNm>
<CcyNm>Loti</CcyNm>
<Ccy>LSL</Ccy>
<CcyNbr>426</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LESOTHO</CtryNm>
<CcyNm>Rand</CcyNm>
<Ccy>ZAR</Ccy>
<CcyNbr>710</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LIBERIA</CtryNm>
<CcyNm>Liberian Dollar</CcyNm>
<Ccy>LRD</Ccy>
<CcyNbr>430</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LIBYA</CtryNm>
<CcyNm>Libyan Dinar</CcyNm>
<Ccy>LYD</Ccy>
<CcyNbr>434</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LIECHTENSTEIN</CtryNm>
<CcyNm>Swiss Franc</CcyNm>
<Ccy>CHF</Ccy>
<CcyNbr>756</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LITHUANIA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>LUXEMBOURG</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MACAO</CtryNm>
<CcyNm>Pataca</CcyNm>
<Ccy>MOP</Ccy>
<CcyNbr>446</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MACEDONIA (THE FORMER YUGOSLAV REPUBLIC OF)</CtryNm>
<CcyNm>Denar</CcyNm>
<Ccy>MKD</Ccy>
<CcyNbr>807</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MADAGASCAR</CtryNm>
<CcyNm>Malagasy Ariary</CcyNm>
<Ccy>MGA</Ccy>
<CcyNbr>969</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MALAWI</CtryNm>
<CcyNm>Malawi Kwacha</CcyNm>
<Ccy>MWK</Ccy>
<CcyNbr>454</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MALAYSIA</CtryNm>
<CcyNm>Malaysian Ringgit</CcyNm>
<Ccy>MYR</Ccy>
<CcyNbr>458</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MALDIVES</CtryNm>
<CcyNm>Rufiyaa</CcyNm>
<Ccy>MVR</Ccy>
<CcyNbr>462</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MALI</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MALTA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MARSHALL ISLANDS (THE)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MARTINIQUE</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MAURITANIA</CtryNm>
<CcyNm>Ouguiya</CcyNm>
<Ccy>MRO</Ccy>
<CcyNbr>478</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MAURITIUS</CtryNm>
<CcyNm>Mauritius Rupee</CcyNm>
<Ccy>MUR</Ccy>
<CcyNbr>480</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MAYOTTE</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>
MEMBER COUNTRIES OF THE AFRICAN DEVELOPMENT BANK GROUP
</CtryNm>
<CcyNm>ADB Unit of Account</CcyNm>
<Ccy>XUA</Ccy>
<CcyNbr>965</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MEXICO</CtryNm>
<CcyNm>Mexican Peso</CcyNm>
<Ccy>MXN</Ccy>
<CcyNbr>484</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MEXICO</CtryNm>
<CcyNm IsFund="true">Mexican Unidad de Inversion (UDI)</CcyNm>
<Ccy>MXV</Ccy>
<CcyNbr>979</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MICRONESIA (FEDERATED STATES OF)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MOLDOVA (THE REPUBLIC OF)</CtryNm>
<CcyNm>Moldovan Leu</CcyNm>
<Ccy>MDL</Ccy>
<CcyNbr>498</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MONACO</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MONGOLIA</CtryNm>
<CcyNm>Tugrik</CcyNm>
<Ccy>MNT</Ccy>
<CcyNbr>496</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MONTENEGRO</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MONTSERRAT</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MOROCCO</CtryNm>
<CcyNm>Moroccan Dirham</CcyNm>
<Ccy>MAD</Ccy>
<CcyNbr>504</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MOZAMBIQUE</CtryNm>
<CcyNm>Mozambique Metical</CcyNm>
<Ccy>MZN</Ccy>
<CcyNbr>943</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>MYANMAR</CtryNm>
<CcyNm>Kyat</CcyNm>
<Ccy>MMK</Ccy>
<CcyNbr>104</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NAMIBIA</CtryNm>
<CcyNm>Namibia Dollar</CcyNm>
<Ccy>NAD</Ccy>
<CcyNbr>516</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NAMIBIA</CtryNm>
<CcyNm>Rand</CcyNm>
<Ccy>ZAR</Ccy>
<CcyNbr>710</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NAURU</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NEPAL</CtryNm>
<CcyNm>Nepalese Rupee</CcyNm>
<Ccy>NPR</Ccy>
<CcyNbr>524</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NETHERLANDS (THE)</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NEW CALEDONIA</CtryNm>
<CcyNm>CFP Franc</CcyNm>
<Ccy>XPF</Ccy>
<CcyNbr>953</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NEW ZEALAND</CtryNm>
<CcyNm>New Zealand Dollar</CcyNm>
<Ccy>NZD</Ccy>
<CcyNbr>554</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NICARAGUA</CtryNm>
<CcyNm>Cordoba Oro</CcyNm>
<Ccy>NIO</Ccy>
<CcyNbr>558</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NIGER (THE)</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NIGERIA</CtryNm>
<CcyNm>Naira</CcyNm>
<Ccy>NGN</Ccy>
<CcyNbr>566</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NIUE</CtryNm>
<CcyNm>New Zealand Dollar</CcyNm>
<Ccy>NZD</Ccy>
<CcyNbr>554</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NORFOLK ISLAND</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NORTHERN MARIANA ISLANDS (THE)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>NORWAY</CtryNm>
<CcyNm>Norwegian Krone</CcyNm>
<Ccy>NOK</Ccy>
<CcyNbr>578</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>OMAN</CtryNm>
<CcyNm>Rial Omani</CcyNm>
<Ccy>OMR</Ccy>
<CcyNbr>512</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PAKISTAN</CtryNm>
<CcyNm>Pakistan Rupee</CcyNm>
<Ccy>PKR</Ccy>
<CcyNbr>586</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PALAU</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PALESTINE, STATE OF</CtryNm>
<CcyNm>No universal currency</CcyNm>
</CcyNtry>
<CcyNtry>
<CtryNm>PANAMA</CtryNm>
<CcyNm>Balboa</CcyNm>
<Ccy>PAB</Ccy>
<CcyNbr>590</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PANAMA</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PAPUA NEW GUINEA</CtryNm>
<CcyNm>Kina</CcyNm>
<Ccy>PGK</Ccy>
<CcyNbr>598</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PARAGUAY</CtryNm>
<CcyNm>Guarani</CcyNm>
<Ccy>PYG</Ccy>
<CcyNbr>600</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PERU</CtryNm>
<CcyNm>Sol</CcyNm>
<Ccy>PEN</Ccy>
<CcyNbr>604</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PHILIPPINES (THE)</CtryNm>
<CcyNm>Philippine Peso</CcyNm>
<Ccy>PHP</Ccy>
<CcyNbr>608</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PITCAIRN</CtryNm>
<CcyNm>New Zealand Dollar</CcyNm>
<Ccy>NZD</Ccy>
<CcyNbr>554</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>POLAND</CtryNm>
<CcyNm>Zloty</CcyNm>
<Ccy>PLN</Ccy>
<CcyNbr>985</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PORTUGAL</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>PUERTO RICO</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>QATAR</CtryNm>
<CcyNm>Qatari Rial</CcyNm>
<Ccy>QAR</Ccy>
<CcyNbr>634</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>RÉUNION</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ROMANIA</CtryNm>
<CcyNm>Romanian Leu</CcyNm>
<Ccy>RON</Ccy>
<CcyNbr>946</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>RUSSIAN FEDERATION (THE)</CtryNm>
<CcyNm>Russian Ruble</CcyNm>
<Ccy>RUB</Ccy>
<CcyNbr>643</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>RWANDA</CtryNm>
<CcyNm>Rwanda Franc</CcyNm>
<Ccy>RWF</Ccy>
<CcyNbr>646</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT BARTHÉLEMY</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA</CtryNm>
<CcyNm>Saint Helena Pound</CcyNm>
<Ccy>SHP</Ccy>
<CcyNbr>654</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT KITTS AND NEVIS</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT LUCIA</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT MARTIN (FRENCH PART)</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT PIERRE AND MIQUELON</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAINT VINCENT AND THE GRENADINES</CtryNm>
<CcyNm>East Caribbean Dollar</CcyNm>
<Ccy>XCD</Ccy>
<CcyNbr>951</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAMOA</CtryNm>
<CcyNm>Tala</CcyNm>
<Ccy>WST</Ccy>
<CcyNbr>882</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAN MARINO</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAO TOME AND PRINCIPE</CtryNm>
<CcyNm>Dobra</CcyNm>
<Ccy>STD</Ccy>
<CcyNbr>678</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SAUDI ARABIA</CtryNm>
<CcyNm>Saudi Riyal</CcyNm>
<Ccy>SAR</Ccy>
<CcyNbr>682</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SENEGAL</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SERBIA</CtryNm>
<CcyNm>Serbian Dinar</CcyNm>
<Ccy>RSD</Ccy>
<CcyNbr>941</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SEYCHELLES</CtryNm>
<CcyNm>Seychelles Rupee</CcyNm>
<Ccy>SCR</Ccy>
<CcyNbr>690</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SIERRA LEONE</CtryNm>
<CcyNm>Leone</CcyNm>
<Ccy>SLL</Ccy>
<CcyNbr>694</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SINGAPORE</CtryNm>
<CcyNm>Singapore Dollar</CcyNm>
<Ccy>SGD</Ccy>
<CcyNbr>702</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SINT MAARTEN (DUTCH PART)</CtryNm>
<CcyNm>Netherlands Antillean Guilder</CcyNm>
<Ccy>ANG</Ccy>
<CcyNbr>532</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>
SISTEMA UNITARIO DE COMPENSACION REGIONAL DE PAGOS "SUCRE"
</CtryNm>
<CcyNm>Sucre</CcyNm>
<Ccy>XSU</Ccy>
<CcyNbr>994</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SLOVAKIA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SLOVENIA</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SOLOMON ISLANDS</CtryNm>
<CcyNm>Solomon Islands Dollar</CcyNm>
<Ccy>SBD</Ccy>
<CcyNbr>090</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SOMALIA</CtryNm>
<CcyNm>Somali Shilling</CcyNm>
<Ccy>SOS</Ccy>
<CcyNbr>706</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SOUTH AFRICA</CtryNm>
<CcyNm>Rand</CcyNm>
<Ccy>ZAR</Ccy>
<CcyNbr>710</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS</CtryNm>
<CcyNm>No universal currency</CcyNm>
</CcyNtry>
<CcyNtry>
<CtryNm>SOUTH SUDAN</CtryNm>
<CcyNm>South Sudanese Pound</CcyNm>
<Ccy>SSP</Ccy>
<CcyNbr>728</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SPAIN</CtryNm>
<CcyNm>Euro</CcyNm>
<Ccy>EUR</Ccy>
<CcyNbr>978</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SRI LANKA</CtryNm>
<CcyNm>Sri Lanka Rupee</CcyNm>
<Ccy>LKR</Ccy>
<CcyNbr>144</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SUDAN (THE)</CtryNm>
<CcyNm>Sudanese Pound</CcyNm>
<Ccy>SDG</Ccy>
<CcyNbr>938</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SURINAME</CtryNm>
<CcyNm>Surinam Dollar</CcyNm>
<Ccy>SRD</Ccy>
<CcyNbr>968</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SVALBARD AND JAN MAYEN</CtryNm>
<CcyNm>Norwegian Krone</CcyNm>
<Ccy>NOK</Ccy>
<CcyNbr>578</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SWAZILAND</CtryNm>
<CcyNm>Lilangeni</CcyNm>
<Ccy>SZL</Ccy>
<CcyNbr>748</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SWEDEN</CtryNm>
<CcyNm>Swedish Krona</CcyNm>
<Ccy>SEK</Ccy>
<CcyNbr>752</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SWITZERLAND</CtryNm>
<CcyNm>Swiss Franc</CcyNm>
<Ccy>CHF</Ccy>
<CcyNbr>756</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SWITZERLAND</CtryNm>
<CcyNm IsFund="true">WIR Euro</CcyNm>
<Ccy>CHE</Ccy>
<CcyNbr>947</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SWITZERLAND</CtryNm>
<CcyNm IsFund="true">WIR Franc</CcyNm>
<Ccy>CHW</Ccy>
<CcyNbr>948</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>SYRIAN ARAB REPUBLIC</CtryNm>
<CcyNm>Syrian Pound</CcyNm>
<Ccy>SYP</Ccy>
<CcyNbr>760</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TAIWAN (PROVINCE OF CHINA)</CtryNm>
<CcyNm>New Taiwan Dollar</CcyNm>
<Ccy>TWD</Ccy>
<CcyNbr>901</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TAJIKISTAN</CtryNm>
<CcyNm>Somoni</CcyNm>
<Ccy>TJS</Ccy>
<CcyNbr>972</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TANZANIA, UNITED REPUBLIC OF</CtryNm>
<CcyNm>Tanzanian Shilling</CcyNm>
<Ccy>TZS</Ccy>
<CcyNbr>834</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>THAILAND</CtryNm>
<CcyNm>Baht</CcyNm>
<Ccy>THB</Ccy>
<CcyNbr>764</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TIMOR-LESTE</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TOGO</CtryNm>
<CcyNm>CFA Franc BCEAO</CcyNm>
<Ccy>XOF</Ccy>
<CcyNbr>952</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TOKELAU</CtryNm>
<CcyNm>New Zealand Dollar</CcyNm>
<Ccy>NZD</Ccy>
<CcyNbr>554</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TONGA</CtryNm>
<CcyNm>Pa’anga</CcyNm>
<Ccy>TOP</Ccy>
<CcyNbr>776</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TRINIDAD AND TOBAGO</CtryNm>
<CcyNm>Trinidad and Tobago Dollar</CcyNm>
<Ccy>TTD</Ccy>
<CcyNbr>780</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TUNISIA</CtryNm>
<CcyNm>Tunisian Dinar</CcyNm>
<Ccy>TND</Ccy>
<CcyNbr>788</CcyNbr>
<CcyMnrUnts>3</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TURKEY</CtryNm>
<CcyNm>Turkish Lira</CcyNm>
<Ccy>TRY</Ccy>
<CcyNbr>949</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TURKMENISTAN</CtryNm>
<CcyNm>Turkmenistan New Manat</CcyNm>
<Ccy>TMT</Ccy>
<CcyNbr>934</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TURKS AND CAICOS ISLANDS (THE)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>TUVALU</CtryNm>
<CcyNm>Australian Dollar</CcyNm>
<Ccy>AUD</Ccy>
<CcyNbr>036</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UGANDA</CtryNm>
<CcyNm>Uganda Shilling</CcyNm>
<Ccy>UGX</Ccy>
<CcyNbr>800</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UKRAINE</CtryNm>
<CcyNm>Hryvnia</CcyNm>
<Ccy>UAH</Ccy>
<CcyNbr>980</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UNITED ARAB EMIRATES (THE)</CtryNm>
<CcyNm>UAE Dirham</CcyNm>
<Ccy>AED</Ccy>
<CcyNbr>784</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>
UNITED KINGDOM OF GREAT BRITAIN AND NORTHERN IRELAND (THE)
</CtryNm>
<CcyNm>Pound Sterling</CcyNm>
<Ccy>GBP</Ccy>
<CcyNbr>826</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UNITED STATES MINOR OUTLYING ISLANDS (THE)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UNITED STATES OF AMERICA (THE)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UNITED STATES OF AMERICA (THE)</CtryNm>
<CcyNm IsFund="true">US Dollar (Next day)</CcyNm>
<Ccy>USN</Ccy>
<CcyNbr>997</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>URUGUAY</CtryNm>
<CcyNm>Peso Uruguayo</CcyNm>
<Ccy>UYU</Ccy>
<CcyNbr>858</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>URUGUAY</CtryNm>
<CcyNm IsFund="true">Uruguay Peso en Unidades Indexadas (URUIURUI)</CcyNm>
<Ccy>UYI</Ccy>
<CcyNbr>940</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>UZBEKISTAN</CtryNm>
<CcyNm>Uzbekistan Sum</CcyNm>
<Ccy>UZS</Ccy>
<CcyNbr>860</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>VANUATU</CtryNm>
<CcyNm>Vatu</CcyNm>
<Ccy>VUV</Ccy>
<CcyNbr>548</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>VENEZUELA (BOLIVARIAN REPUBLIC OF)</CtryNm>
<CcyNm>Bolívar</CcyNm>
<Ccy>VEF</Ccy>
<CcyNbr>937</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>VIET NAM</CtryNm>
<CcyNm>Dong</CcyNm>
<Ccy>VND</Ccy>
<CcyNbr>704</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>VIRGIN ISLANDS (BRITISH)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>VIRGIN ISLANDS (U.S.)</CtryNm>
<CcyNm>US Dollar</CcyNm>
<Ccy>USD</Ccy>
<CcyNbr>840</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>WALLIS AND FUTUNA</CtryNm>
<CcyNm>CFP Franc</CcyNm>
<Ccy>XPF</Ccy>
<CcyNbr>953</CcyNbr>
<CcyMnrUnts>0</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>WESTERN SAHARA</CtryNm>
<CcyNm>Moroccan Dirham</CcyNm>
<Ccy>MAD</Ccy>
<CcyNbr>504</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>YEMEN</CtryNm>
<CcyNm>Yemeni Rial</CcyNm>
<Ccy>YER</Ccy>
<CcyNbr>886</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZAMBIA</CtryNm>
<CcyNm>Zambian Kwacha</CcyNm>
<Ccy>ZMW</Ccy>
<CcyNbr>967</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZIMBABWE</CtryNm>
<CcyNm>Zimbabwe Dollar</CcyNm>
<Ccy>ZWL</Ccy>
<CcyNbr>932</CcyNbr>
<CcyMnrUnts>2</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ01_Bond Markets Unit European_EURCO</CtryNm>
<CcyNm>Bond Markets Unit European Composite Unit (EURCO)</CcyNm>
<Ccy>XBA</Ccy>
<CcyNbr>955</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ02_Bond Markets Unit European_EMU-6</CtryNm>
<CcyNm>
Bond Markets Unit European Monetary Unit (E.M.U.-6)
</CcyNm>
<Ccy>XBB</Ccy>
<CcyNbr>956</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ03_Bond Markets Unit European_EUA-9</CtryNm>
<CcyNm>
Bond Markets Unit European Unit of Account 9 (E.U.A.-9)
</CcyNm>
<Ccy>XBC</Ccy>
<CcyNbr>957</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ04_Bond Markets Unit European_EUA-17</CtryNm>
<CcyNm>
Bond Markets Unit European Unit of Account 17 (E.U.A.-17)
</CcyNm>
<Ccy>XBD</Ccy>
<CcyNbr>958</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ06_Testing_Code</CtryNm>
<CcyNm>Codes specifically reserved for testing purposes</CcyNm>
<Ccy>XTS</Ccy>
<CcyNbr>963</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ07_No_Currency</CtryNm>
<CcyNm>
The codes assigned for transactions where no currency is involved
</CcyNm>
<Ccy>XXX</Ccy>
<CcyNbr>999</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ08_Gold</CtryNm>
<CcyNm>Gold</CcyNm>
<Ccy>XAU</Ccy>
<CcyNbr>959</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ09_Palladium</CtryNm>
<CcyNm>Palladium</CcyNm>
<Ccy>XPD</Ccy>
<CcyNbr>964</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ10_Platinum</CtryNm>
<CcyNm>Platinum</CcyNm>
<Ccy>XPT</Ccy>
<CcyNbr>962</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
<CcyNtry>
<CtryNm>ZZ11_Silver</CtryNm>
<CcyNm>Silver</CcyNm>
<Ccy>XAG</Ccy>
<CcyNbr>961</CcyNbr>
<CcyMnrUnts>N.A.</CcyMnrUnts>
</CcyNtry>
</CcyTbl>
</ISO_4217>
"""
ISO_currencies = {cur.findtext("Ccy"): ISO_type(*[e.text for e in cur.getchildren()])
                  for cur in ElementTree.fromstring(ISO_currencies_XML).findall(".//CcyNtry")
                  if cur.findtext("CcyMnrUnts")
                  }
