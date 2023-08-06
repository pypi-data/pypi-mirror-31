# SonicParanoid: very fast, accurate, and easy orthology #

SonicParanoid is a stand-alone software tool for the identification of orthologous relationships among multiple species.

It was developed at [Iwasaki-lab](http://iwasakilab.bs.s.u-tokyo.ac.jp) at [The University of Tokyo](http://www.u-tokyo.ac.jp/en/index.html).

A more user friendly description of the method and its use can be found at the [`sonicparanoid web-page`](http://iwasakilab.bs.s.u-tokyo.ac.jp/sonicparanoid)

## Fast ##

SonicParanoid, executed in the fast mode, predicted orthologous relationships for 40 eukaryotic proteomes in about 70 minutes, or in less than 5 minutes for 26 prokaryotes, using only 8 CPUs. Moreover it processed the InParanoid8 input dataset, composed of 273 proteomes (246 eukaryotes), in about one and a half days (38 hours).


## Accurate ##

SonicParanoid was tested using a benchmark proteome dataset from [the Quest for Orthologs consortium](http://questfororthologs.org), and the correctness of its predictions was evaluated using a public Orthology Benchmarking service. When compared to other 13 orthology prediction tools, SonicParanoid showed a [balanced trade-off between precision and recall](http://orthology.benchmarkservice.org/cgi-bin/gateway.pl?f=CheckResults&p1=72d29d4aebb02e0d396fcad2), with an accuracy comparable to those of well-established inference methods.


## Easy to use ##

SonicParanoid only requires the Python programming language and the MMseqs2 alignment tool, to be installed in your laptop/server in order to work. The low hardware requirements make it possible to run SonicParanoid on modern laptop computers, while the "update" feature allows users to easily maintain collections of orthologs that can be updated by adding or removing species.


## License ##
Copyright � 2017, Salvatore Cosentino, [The University of Tokyo](http://www.u-tokyo.ac.jp/en/index.html) All rights reserved.

Licensed under the GNU GENERAL PUBLIC LICENSE, Version 3.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
[https://www.gnu.org/licenses/gpl-3.0.en.html](https://www.gnu.org/licenses/gpl-3.0.en.html)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an __"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND__, either express or implied. See the License for the specific language governing permissions and limitations under the License.

## Contact ##
`Salvatore Cosentino`

* salvocos@bs.s.u-tokyo.ac.jp
* salvo981@gmail.com

`Wataru Iwasaki`

* email: iwasaki@bs.s.u-tokyo.ac.jp
* web-page: [Iwasaki-lab](http://iwasakilab.bs.s.u-tokyo.ac.jp/eindex.html)
