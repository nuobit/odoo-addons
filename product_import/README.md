<section class="oe_container oe_dark">
    <div class="oe_row oe_spaced">
        <div class="oe_span12">
            <h2 class="oe_slogan"><span style="color:#3b5998">Product Import</span></h2>
            <h3 class="oe_slogan"><span style="color:#616161">Import and massive update products</span></h3>
        </div>
        <div class="oe_span12 oe_mt16">
            <div class="oe_demo oe_screenshot">
                <img src="static/description/1.jpg">
            </div>
        </div>
    </div>
    <div class="oe_row oe_spaced">
        <div class="oe_span12">
            <p>
                Add entry <strong>Import Products</strong> in Product menu of <i>Sales</i>, <i>Purchase</i> and <i>Warehouse</i> applications.
                It only can
                be viewed by <i>Sales Manager</i>, <i>Purchase Manager</i> and <i>Warehouse Manager</i>
            </p>
        </div>
            <div class="oe_span12">
            <div class="oe_demo oe_picture oe_screenshot">
                <img src="static/description/2.jpg" >
            </div>
        </div>
    </div>

</section>
<section class="oe_container">
    <div class="oe_row oe_spaced">
        <div>
            <h2 class="oe_slogan"><span style="color:#3b5998">How to use it</span></h2>
        </div>
        <div class="oe_span12">
            <ul style="list-style-type:disc">
                <li>Write a <strong>Description.</strong></li>
                <li>
                    <span><strong>Select</strong> CSV file.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/3.jpg">
                    </div>
                </li>
                <li>
                    <span><strong>Load Header</strong> to load the file's first row and populate the mapping fields. Each selection field contains all the titles of the file.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/4.jpg">
                    </div>
                </li>
                <li>
                    <span>Remap file headers if it's necessary. The <i>Reference</i> field determines if product exists.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/5.jpg">
                    </div>
                </li>
                <li>
                    <span><strong>Load data</strong> to populate the grid below according to mapped fields.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/6.jpg">
                    </div>
                </li>
                <li>
                    <span>Select the <strong>Supplier</strong> in case you need to update <i>Purchase Pricelist</i> or create products with new <i>Purchase
                        Pricelist</i>.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/7.jpg">
                    </div>
                </li>
                <li>
                    <span>In case the product already exists you can select which field to update in <strong>Update
                        options</strong> tab.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/8.jpg">
                    </div>
                    <span>If <i>Update Category</i> is selected the <i>Create Category</i> option is enabled. It allows to create a category in case the <i>Product</i> exists but the <i>Category</i> doesn't.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/9.jpg">
                    </div>
                </li>
                <li>
                    <span>In case the product does not exist you can select if it must be created and how in <strong>Create
                        options</strong> tab.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/10.jpg">
                    </div>
                    <ul>
                        <li><strong>Create Product</strong> allow create product if not exists. When enabled the
                            rest of options are shown.
                            <div class="oe_demo oe_picture oe_screenshot">
                                <img src="static/description/11.jpg">
                            </div>
                            <ul>
                                <li><strong>Create Category</strong> Allow create category if not exists.</li>
                                <li><strong>Create always Supplier Info</strong> Allow create product with the
                                    <i>Supplier</i> selected
                                    even if the <i>Purchase Pricelist</i> is not defined.
                                </li>
                                <li><strong>Create without Supplier Info</strong> Allow create product if neither
                                    <i>Supplier</i>
                                    nor <i>Purchase Pricelist</i> are defined.
                                </li>
                            </ul>
                        </li>
                    </ul>
                </li>
                <li>
                    <span>If the product will be created, in the <strong>Creation options</strong> tab you can define default values.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/12.jpg">
                    </div>
                </li>
                <li>
                    <span>Select file and system options in <strong>Other options</strong> tab.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/13.jpg">
                    </div>
                    <ul>
                        <li><strong>Delimiter</strong> Character used to delimiter fields in CSV file.</li>
                        <li><strong>Quotechar</strong> Character used to quote text fields.</li>
                        <li><strong>Strip values</strong> Remove field leading and trailing spaces.</li>
                        <li><strong>Round</strong> Number of decimals to round <i>Sale Pricelist</i> and <i>Purchase
                            Pricelist.</i></li>
                        <li><strong>Encoding</strong> Define file encoding.</li>
                        <li><strong>Timeout</strong> Avoid reverse proxy or web server timeout. After this number of
                            seconds, the import process will be put on hold and it will be able to continue after
                            error correction and removing done lines.
                        </li>
                    </ul>
                </li>
                <li>
                    <span>Press the <strong>Update</strong> button to start de import process. Maximum execution time is <strong>Timeout</strong> seconds.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/14.jpg">
                    </div>
                </li>
                <li>
                    <span>When the import process finish:</span>
                    <ul>
                        <li>Each line will be populad with <strong>Status</strong> of the process for that line
                            (<i>Done</i> or <i>Error</i>) and <strong>Observations</strong> indicating if there was a
                            problem and how to solve it.
                        </li>
                        <li>The progress bar indicates the percentage of import done. In case the
                            <i>Timeout</i> was reached it shows less than 100%.
                        </li>
                    </ul>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/15.jpg">
                    </div>
                </li>
                <li>
                    <span>Use <strong>Remove done</strong> button to remove all lines processed successfully (with done status). If there's still errors, modifiy the importing parameters according to the observations and press the <strong>Update</strong> button again. Repeat the process until all errors are gone.</span>
                    <div class="oe_demo oe_picture oe_screenshot">
                        <img src="static/description/16.jpg">
                    </div>
                </li>
            </ul>
        </div>
    </div>
</section>