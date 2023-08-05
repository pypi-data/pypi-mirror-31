import React, { PureComponent } from 'react';
import PropTypes from 'prop-types';
import Table from './Table';
import Row from './Row';
import Cell from './Cell';

var JSONPretty = require('react-json-pretty');
var elementResizeEvent = require('element-resize-event');

class StickyTable extends PureComponent {
  static propTypes = {
    stickyHeaderCount: PropTypes.number,
    stickyColumnCount: PropTypes.number,
    onScroll: PropTypes.func
  };

  static defaultProps = {
    stickyHeaderCount: 1,
    stickyColumnCount: 1
  };

  constructor(props) {
    super(props);

    this.id = Math.floor(Math.random() * 1000000000) + '';

    this.rowCount = 0;
    this.columnCount = 0;
    this.xScrollSize = 0;
    this.yScrollSize = 0;
    this.stickyHeaderCount = props.stickyHeaderCount === 0 ? 0 : (this.stickyHeaderCount || 1);
    this.container_ref = React.createRef();

    this.isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;
  }

  componentDidMount() {
    this.table = document.getElementById('sticky-table-' + this.id);

    if (this.table) {
      this.realTable = this.table.querySelector('#sticky-table-x-wrapper').firstChild;
      this.xScrollbar = this.table.querySelector('#x-scrollbar');
      this.yScrollbar = this.table.querySelector('#y-scrollbar');
      this.xWrapper = this.table.querySelector('#sticky-table-x-wrapper');
      this.yWrapper = this.table.querySelector('#sticky-table-y-wrapper');
      this.stickyHeader = this.table.querySelector('#sticky-table-header');
      this.stickyColumn = this.table.querySelector('#sticky-table-column');
      this.stickyCorner = this.table.querySelector('#sticky-table-corner');
      this.setScrollData();

      elementResizeEvent(this.realTable, this.onResize);

      this.onResize();
      setTimeout(this.onResize);
      this.addScrollBarEventHandlers();
      this.scrollToValue();
    }
  }

  componentDidUpdate() {
    this.scrollToValue();
    this.onResize();
      
    var header_elements = document.getElementsByClassName("header_element");
    
    for(var v = 0; v < header_elements.length; v++){
        header_elements[v].style.height = this.getModeHeights() + "px";
    }
  }

  componentWillUnmount() {
    if (this.table) {
      this.xWrapper.removeEventListener('scroll', this.onScrollX);
      this.xWrapper.removeEventListener('scroll', this.scrollXScrollbar);
      this.xScrollbar.removeEventListener('scroll', this.onScrollBarX);

      this.yWrapper.removeEventListener('scroll', this.scrollYScrollbar);
      this.yScrollbar.removeEventListener('scroll', this.onScrollBarY);

      elementResizeEvent.unbind(this.realTable);
    }
  }

  scrollToValue = () => {
    var element = document.getElementsByClassName("header_element");

    for(var x = 0; x < element.length; x++){
        if(element[x].innerText == this.scrollVal || element[x].innerText == this.props.scrollVal){
            this.yScrollbar.scrollTop = element[x].offsetTop - element[x].offsetHeight - 6;
            this.scrollVal = -1;
            this.props.scrollVal = -1;
            break;
        }
    }
      
    this.props.reset_scroll(this.props.parent_context);
  }

  addScrollBarEventHandlers() {
    this.xWrapper.addEventListener('scroll', this.onScrollX);

    //X Scrollbars
    this.xWrapper.addEventListener('scroll', this.scrollXScrollbar);
    this.xScrollbar.addEventListener('scroll', this.onScrollBarX);

    //Y Scrollbars
    this.yWrapper.addEventListener('scroll', this.scrollYScrollbar);
    this.yScrollbar.addEventListener('scroll', this.onScrollBarY);
  }

  setScrollData = () => {
    this.suppressScrollX = false;
    this.suppressScrollY = false;

    return this.scrollData = {
      scrollTop: this.yScrollbar.scrollTop,
      scrollHeight: this.yScrollbar.scrollHeight,
      clientHeight: this.yScrollbar.clientHeight,
      scrollLeft: this.xScrollbar.scrollLeft,
      scrollWidth: this.xScrollbar.scrollWidth,
      clientWidth: this.xScrollbar.clientWidth
    };
  }

  onScrollBarX = () => {
    if (!this.suppressScrollX) {
      this.scrollData.scrollLeft = this.xWrapper.scrollLeft = this.xScrollbar.scrollLeft;
      this.suppressScrollX = true;
    } else {
      this.handleScroll();
      this.suppressScrollX = false;
    }
  }

  onScrollBarY = () => {
    if (!this.suppressScrollY) {
      this.scrollData.scrollTop = this.yWrapper.scrollTop = this.yScrollbar.scrollTop;
      this.suppressScrollY = true;
    } else {
      this.handleScroll();
      this.suppressScrollY = false;
    }
  }

  onScrollX = () => {
    var scrollLeft = Math.max(this.xWrapper.scrollLeft, 0);
    this.stickyHeader.style.transform = 'translate(' + (-1 * scrollLeft) + 'px, 0)';
  }

  scrollXScrollbar = () => {
    if (!this.suppressScrollX) {
      this.scrollData.scrollLeft = this.xScrollbar.scrollLeft = this.xWrapper.scrollLeft;
      this.suppressScrollX = true;
    } else {
      this.handleScroll();
      this.suppressScrollX = false;
    }
  }

  scrollYScrollbar = () => {
    if (!this.suppressScrollY) {
      this.scrollData.scrollTop = this.yScrollbar.scrollTop = this.yWrapper.scrollTop;
      this.suppressScrollY = true;
    } else {
      this.handleScroll();
      this.suppressScrollY = false;
    }
  }

  handleScroll = () => {
    if (this.props.onScroll) {
      this.props.onScroll(this.scrollData);
    }
    
    var scroll_down = this.getScrollBottom();
    var scroll_up = this.getScrollTop();
      
    if(scroll_down == 1){
      this.updateScrollDown();
    }

    if(scroll_up == 0){
      this.updateScrollUp();
    }
  }
    
  updateScrollDown = () => {
    if(this.props.set_higher*this.props.step_size >= this.props.size){
      return "Max value reached";
    }else if(this.props.scroll_state){
      var element = document.getElementsByClassName("header_element");
      if(element.length > 0){
          
        var element_to_jump = element[element.length - 1].innerText;
        
        for(var v = 0; v < element.length; v++){
            var bounding_rectangle = element[v].getBoundingClientRect();
            if(bounding_rectangle.top > 0){
                element_to_jump = element[v].innerText;
                break;
            }
        };
        
        this.scrollVal = element_to_jump;
        this.props.scroll_callback(this.scrollVal, this.props.parent_context, 1);
      }
    }
  }

  updateScrollUp = () => {
    if(this.props.set_lower*this.props.step_size <= 0){
      return "Min value reached";
    }else if(this.props.scroll_state){
      var element = document.getElementsByClassName("header_element");

      if(element.length > 0){
        this.scrollVal = parseInt(element[0].innerText, 10);
        this.props.scroll_callback(this.scrollVal, this.props.parent_context, -1);
      }
    }
  }

  getScrollBottom = () => {
    return (this.yScrollbar.scrollTop + this.yScrollbar.clientHeight)/this.yScrollbar.scrollHeight;
  }

  getScrollTop = () => {
    return (this.yScrollbar.scrollTop)/this.yScrollbar.scrollHeight;
  }

  getRows = (start_index, end_index) => {
    this.scroll = false;
  }
    
  onResize = () => {
    this.setScrollBarDims();
    this.setScrollBarWrapperDims();
    this.setRowHeights();
    this.setColumnWidths();
    this.setScrollData();
    this.handleScroll();
  }

  setScrollBarPaddings() {
    var scrollPadding = '0px 0px ' + this.xScrollSize + 'px 0px';
    this.table.style.padding = scrollPadding;

    var scrollPadding = '0px ' + this.yScrollSize + 'px 0px 0px';
    this.xWrapper.firstChild.style.padding = scrollPadding;
  }

  setScrollBarWrapperDims = () => {
    this.xScrollbar.style.width = 'calc(100% - ' + this.yScrollSize + 'px)';
    this.yScrollbar.style.height = 'calc(100% - ' + this.stickyHeader.offsetHeight + 'px)';
    this.yScrollbar.style.top = this.stickyHeader.offsetHeight + 'px';
  }

  setScrollBarDims() {
    this.xScrollSize = this.xScrollbar.offsetHeight - this.xScrollbar.clientHeight;
    this.yScrollSize = this.yScrollbar.offsetWidth - this.yScrollbar.clientWidth;

    if (!this.isFirefox) {
      this.setScrollBarPaddings();
    }

    var width = this.getSize(this.realTable.firstChild).width;
    this.xScrollbar.firstChild.style.width = width + 'px';

    var height = this.getSize(this.realTable).height + this.xScrollSize - this.stickyHeader.offsetHeight;
    this.yScrollbar.firstChild.style.height = height + 'px';

    if (this.xScrollSize) this.xScrollbar.style.height = this.xScrollSize + 1 + 'px';
    if (this.yScrollSize)  this.yScrollbar.style.width = this.yScrollSize + 1  + 'px';
  }

  getModeHeights(){
    var mode = function mode(arr) {
      var numMapping = {};
      var greatestFreq = 0;
      var mode;
      arr.forEach(function findMode(number) {
          numMapping[number] = (numMapping[number] || 0) + 1;

          if (greatestFreq < numMapping[number]) {
              greatestFreq = numMapping[number];
              mode = number;
          }
      });
      return +mode;
    }

    var heights = [];
      
    if (this.props.stickyColumnCount) {
      for (var r = 0; r < this.rowCount; r++) {
        heights.push(this.getSize(this.realTable.childNodes[r].childNodes[0]).height)
      }
    }

    return mode(heights);
  }

  setRowHeights() {
    var r, c, cellToCopy, height;

    var row_value = (this.props.y != undefined)?this.props.y:-1;
    var column_offset_top = 0;
      
    if (this.props.stickyColumnCount) {
      for (r = 1; r < this.rowCount; r++) {
        cellToCopy = this.realTable.childNodes[r].firstChild;
        if (cellToCopy) {
          this.realTable.childNodes[r].childNodes[1].style.height = this.getModeHeights() + "px";
          this.stickyColumn.firstChild.childNodes[r].style.height = this.getModeHeights() + "px";
          height = this.getSize(cellToCopy).height;
          this.stickyColumn.firstChild.childNodes[r].firstChild.style.height = height + 'px';
        
          if (r == 0 && this.stickyCorner.firstChild.childNodes[r]) {
            this.stickyCorner.firstChild.firstChild.firstChild.style.height = height + 'px';
          }
        }
        
        if(row_value == r){
            column_offset_top  = this.stickyColumn.firstChild.childNodes[r].offsetTop;
        }
      }
      this.stickyCorner.firstChild.firstChild.firstChild.style.height = this.stickyHeader.offsetHeight + 'px';
      this.stickyColumn.firstChild.childNodes[0].firstChild.style.height = this.stickyHeader.offsetHeight+'px';
    
      
        if(document.getElementById("data_container")){
            document.getElementById("data_container").style.height =  this.getModeHeights()*3 - 30 + "px"
            document.getElementById("data_container").style.width = (this.xScrollbar.clientWidth - 30) + "px";
            document.getElementById("data_container").style.left = 15 + "px";
            document.getElementById("data_container").style.top = column_offset_top + this.getModeHeights() + 15 + "px";
        }
    }
  }

  setColumnWidths() {
    var c, cellToCopy, cellStyle, width, cell, stickyWidth;

    if (this.stickyHeaderCount) {
      stickyWidth = 0;

      for (c = 0; c < this.columnCount; c++) {
        cellToCopy = this.realTable.firstChild.childNodes[c];

        if (cellToCopy) {
          width = this.getSize(cellToCopy).width;

          cell = this.table.querySelector('#sticky-header-cell-' + c);

          cell.style.width = width + 'px';
          cell.style.minWidth = width + 'px';

          const fixedColumnsHeader = this.stickyCorner.firstChild.firstChild;
          if (fixedColumnsHeader && fixedColumnsHeader.childNodes[c]) {
            cell = fixedColumnsHeader.childNodes[c];
            cell.style.width = width + 'px';
            cell.style.minWidth = width + 'px';

            cell = fixedColumnsHeader.childNodes[c];
            cell.style.width = width + 'px';
            cell.style.minWidth = width + 'px';
            stickyWidth += width;
          }
        }
      }

      this.stickyColumn.firstChild.style.width = stickyWidth + 'px';
      this.stickyColumn.firstChild.style.minWidth = stickyWidth + 'px';
    }
  }

  getStickyColumns(rows) {
    const columnsCount = this.props.stickyColumnCount;
    var cells;
    var stickyRows = [];
    var row_value = (this.props.y != undefined)?parseInt(this.props.y, 10):-1;
      
      
    if(this.props.scrollVal != -1){
      this.scroll = false;
    }

    rows.forEach((row, r) => {
      cells = React.Children.toArray(row.props.children);
      if(row.props.accordion && row_value > 0) {
        if(this.props.data){
          var one_indexed = this.props.data.index  + 1;
          if(one_indexed == parseInt(this.props.y, 10) && this.props.data.column == this.props.column_name && this.props.column_name != undefined){
            var data_entries = [];
            switch (this.props.data.type) {
              case window.flex_type_enum.string:
                data_entries.push(<div style={{"word-wrap": "break-word"}}>{this.props.data.data}</div>);
                break;
              case window.flex_type_enum.dict:
              case window.flex_type_enum.vector:
              case window.flex_type_enum.list:
              case window.flex_type_enum.nd_vector:
                data_entries.push(<JSONPretty className="json-pretty" json={this.props.data.data}></JSONPretty>);
                break;
              default:
                break;
            }

            stickyRows.push(
              <Row {...row.props}>
                  <div id="data_container" style={{"position": "absolute", "overflow": "scroll", "width": 100, "left": 3, "zIndex": 99, "textAlign": "left", "background": "#F7F7F7"}}>
                  <div style={{"padding": 10}}>
                    {data_entries}
                  </div>
                </div>
              </Row>
            );
          }else{
            stickyRows.push(
              <Row {...row.props}>
                <div id="data_container" style={{"position": "absolute", "overflow": "scroll", "width": 100, "left": 3, "zIndex": 99, "textAlign": "left", "background": "#F7F7F7"}}>
                  <div style={{"padding": 10}}>
                    Loading...
                  </div>
                </div>
              </Row>
            );
          }
        }else{
          stickyRows.push(
            <Row {...row.props}>
              <div id="data_container" style={{"position": "absolute", "overflow": "scroll", "width": 100, "left": 3, "zIndex": 99, "textAlign": "left", "background": "#F7F7F7"}}>
                <div style={{"padding": 10}}>
                  Loading...
                </div>
              </div>
            </Row>
          );
        }
      } else if(row.props.spacers && row_value > 0) {
        stickyRows.push(
          <Row {...row.props} key={r}>
            {cells.slice(0, columnsCount)}
          </Row>
        );
      }else{
        stickyRows.push(
          <Row {...row.props} id='' key={r}>
            {cells.slice(0, columnsCount)}
          </Row>
        );
      }
    });

    return stickyRows;
  }

  getStickyHeader(rows) {
    var row = rows[0];
    var cells = [];

    React.Children.toArray(row.props.children).forEach((cell, c) => {
      cells.push(React.cloneElement(cell, {id: 'sticky-header-cell-' + c, key: c}));
    });

    return (
      <Row {...row.props} id='sticky-header-row'>
        {cells}
      </Row>
    );
  }

  getStickyCorner(rows) {
    const columnsCount = this.props.stickyColumnCount;
    var cells;
    var stickyCorner = [];

    rows.forEach((row, r) => {
      if (r === 0) {
        cells = React.Children.toArray(row.props.children);

        stickyCorner.push(
          <Row {...row.props} id='' key={r}>
            {cells.slice(0, columnsCount)}
          </Row>
        );
      }
    });
    return stickyCorner;
  }

  getSize(node) {
    var width = node ? node.getBoundingClientRect().width : 0;
    var height = node ? node.getBoundingClientRect().height : 0;

    return {width, height};
  }

  render() {
    var rows = React.Children.toArray(this.props.children);
    var stickyColumn, stickyHeader, stickyCorner;

    this.rowCount = rows.length;
    this.columnCount = (rows[0] && React.Children.toArray(rows[0].props.children).length) || 0;
      
    if (rows.length) {
      if (this.props.stickyColumnCount > 0 && this.stickyHeaderCount > 0) {
        stickyCorner = this.getStickyCorner(rows);
      }
      if (this.props.stickyColumnCount > 0) {
        stickyColumn = this.getStickyColumns(rows);
      }
      if (this.stickyHeaderCount > 0) {
        stickyHeader = this.getStickyHeader(rows);
      }
    }
      
    return (
      <div className={'sticky-table ' + (this.props.className || '')} id={'sticky-table-' + this.id}>
        <div id='x-scrollbar'><div></div></div>
        <div id='y-scrollbar'><div></div></div>
        <div className='sticky-table-corner' id='sticky-table-corner'>
          <Table>{stickyCorner}</Table>
        </div>
        <div className='sticky-table-header' id='sticky-table-header'>
          <Table>{stickyHeader}</Table>
        </div>
        <div className='sticky-table-y-wrapper' id='sticky-table-y-wrapper'>
          <div className='sticky-table-column' id='sticky-table-column'>
            <Table>{stickyColumn}</Table>
          </div>
          <div className='sticky-table-x-wrapper' id='sticky-table-x-wrapper'>
            <Table>{rows}</Table>
          </div>
        </div>
      </div>
    );
  }
}

export {StickyTable, Table, Row, Cell};
                                var image_bound_height = parseInt(((element_bounding.height/2 - image_bounding.height/2) + (element_bounding.y)), 10);

                                                                    var header_positon = document.getElementsByClassName("header")[0].getBoundingClientRect();
                                                                    var header_top = header_positon.y + header_positon.height;

                                                                    var footer_position = document.getElementsByClassName("BottomTable")[0].getBoundingClientRect();
                                                                    var footer_top = footer_position.y;

                                                                    if(header_top > image_bound_height){
                                                                        image_bound_height = header_top;
                                                                    }

                                                                    if((image_bound_height+image_bounding.height) > footer_top){
                                                                        image_bound_height = footer_top - image_bounding.height;
                                                                    }

                                                                    $this.image_source_container.style.top = image_bound_height + "px";

                                                                    var right_value = (element_bounding.width + element_bounding.left);
                                                                    var right_image = (element_bounding.width + element_bounding.left + 10);

                                                                    $this.arrow_left.style.left = right_value + "px";
                                                                    $this.image_source_container.style.left = right_image +"px";

                                                                    clearInterval($this.loading_image_timer);

                                                                 }
                                                             }
                                                         }, 300, imageRow, imageColumn, target);
          }
        }
      }
    }
  }

  hoverOutImage(result){
    var $this = this;
    return function(e) {
      if(result == "image"){
        if($this.image_source_container != null && e.target.getElementsByTagName("img")[0] && e.target.classList.contains('elements')){
          $this.image_source_container.src = "";
        }
      }
      if($this.loading_image_timer){
        clearInterval($this.loading_image_timer);
      }

      $this.image_source_container.style.display = "none";
      $this.image_loading_container.style.display = "none";
      $this.arrow_left.style.display = "none";
    }
  }

  divClick(e){
    var dict_elements = {};
    dict_elements["target"] = (e.target.parentElement.parentElement);
    this.cellClick(dict_elements);
  }

  spanClick(e){
    var dict_elements = {};
    dict_elements["target"] = (e.target.parentElement.parentElement.parentElement);
    this.cellClick(dict_elements);
  }

  arrowClick(e){
    var dict_elements = {};
    dict_elements["target"] = (e.target.parentElement.parentElement);
    this.cellClick(dict_elements);
  }

  cellClick(e){
    var row_number = e.target.getAttribute("x");
    var column_name = e.target.getAttribute("y");
    var type = e.target.getAttribute("flex_type");

    switch (type) {
      case "string":
      case "dictionary":
      case "array":
      case "ndarray":
      case "list":
        var active_element_loop = e.target.parentElement.parentElement.getElementsByClassName("active_element");

        for(var ele = 0; ele < active_element_loop.length; ele++){
          if(active_element_loop[ele] != e.target){
            active_element_loop[ele].children[0].children[1].children[0].style.display = "block";
            active_element_loop[ele].children[0].children[1].children[1].style.display = "none";
            active_element_loop[ele].children[0].children[1].classList.remove("active_arrow");
            active_element_loop[ele].classList.remove("active_element");
          }
        }


        if(e.target.children[0].children[0].getBoundingClientRect().width < e.target.children[0].children[0].children[0].getBoundingClientRect().width){

          if(e.target.children[0].children[1].children[0].style.display == "none"){
            e.target.children[0].children[1].children[0].style.display = "block";
            e.target.children[0].children[1].children[1].style.display = "none";
            e.target.classList.remove("active_element");
            e.target.children[0].children[1].classList.remove("active_arrow");
            this.data_sent = undefined;
            this.column_name = undefined;
            this.y = -1;
            this.drawTable();
          }else{
            e.target.children[0].children[1].children[0].style.display = "none";
            e.target.children[0].children[1].children[1].style.display = "block";
            e.target.classList.add("active_element");
            e.target.children[0].children[1].classList.add("active_arrow");
            this.data_sent = undefined;
            this.column_name = undefined;
            this.y = -1;

            var column_name_str = column_name.replace('"', "\\\"");

            this.drawTable(true, row_number, column_name, column_name_str);
          }
        }

        break;
      case "image":
        break;
      default:
        break;
    }
  }

  drawTable(callback_accordion = false, y = -1, column_name = undefined, column_name_str = undefined){

    var rows = [];
    var row_ids = [];

    this.table_array = [];

    for (var r = 0; r < this.data.values.length+1; r++) {
      var cells = [];
      for (var c = 0; c < this.table_spec["column_names"].length+1; c++) {
        if(c === 0){
          if(r === 0){
            cells.push(<Cell className="header" key={c+"_"+r}></Cell>);
          }else{
            cells.push(<Cell className="header_element" key={c+"_"+r}>{this.data.values[r-1]["__idx"]}</Cell>);
            row_ids.push(this.data.values[r-1]["__idx"]);
          }
        }else{
          if(r === 0){
            cells.push(<Cell className={"header"} key={c+"_"+r}><span>{this.table_spec["column_names"][c-1]}</span></Cell>);
          }else{
            var element_type = this.table_spec["column_types"][c-1];
            var element_column_name = this.table_spec["column_names"][c-1];
            cells.push(<Cell className="elements" onMouseEnter={this.hoverImage(this.table_spec["column_types"][c-1])} onMouseLeave={this.hoverOutImage(this.table_spec["column_types"][c-1])} onClick={(e) => this.cellClick(e)} x={r} x_c={c} y={element_column_name} flex_type={element_type} key={c+"_"+r}>{ this.renderCell(this.data.values[r-1][element_column_name], element_type )}</Cell>);
          }
        }
      }
      rows.push(<Row key={r}>{cells}</Row>);

      if(this.y == r){
        var empty_cells = [];
        empty_cells.push(<Cell className={"header_element accordion_helper"} key={"0_"+r+"modal"}>&nbsp;</Cell>);

        for(var x = 1; x < cells.length;x++){
          empty_cells.push(<Cell className={"elements accordion_helper"} key={x+"_"+r+"modal"}>&nbsp;</Cell>);
        }

        rows.push(<Row key={"modal"} accordion={true}>
                    {empty_cells}
                  </Row>);

        var empty_cells_1 = [];
        empty_cells_1.push(<Cell className={"header_element accordion_helper"} key={"0_"+r+"spacer1"}>&nbsp;</Cell>);

        for(var x = 1; x < cells.length;x++){
          empty_cells_1.push(<Cell className={"elements accordion_helper"} key={x+"_"+r+"spacer1"}>&nbsp;</Cell>);
        }

        rows.push(<Row key={"spacer1"} spacers={true}>
                    {empty_cells_1}
                  </Row>);

        var empty_cells_2 = [];
        empty_cells_2.push(<Cell className={"header_element accordion_helper"} key={"0_"+r+"spacer2"}>&nbsp;</Cell>);

        for(var x = 1; x < cells.length;x++){
          empty_cells_2.push(<Cell className={"elements accordion_helper"} key={x+"_"+r+"spacer2"}>&nbsp;</Cell>);
        }

        rows.push(<Row key={"spacer2"} spacers={true}>
                    {empty_cells_2}
                  </Row>);
      }
    }

      
    var n = Math.floor(Math.min(...row_ids)/this.step_size);
      
    this.set_higher = n + 2;
    this.set_lower = n;
      
    var parent_context = this;

    if(this.title != ""){
      var tableTitle = (
                          <h1 className="tableTitle"  key="tableTitle">
                            {this.title}
                          </h1>
                        );
      this.table_array.push(tableTitle);
    }

    var tableBody = (
                      <div className="resize_container" key="tableBody" style={{ "height": this.state.windowHeight-44, "width": this.state.windowWidth}}>
                     <StickyTable parent_context={parent_context} scroll_state={this.table_scroll} scrollVal={this.scrollVal} size={this.size} step_size={this.step_size} set_lower={this.set_lower} set_higher={this.set_higher}  y={this.y} data={this.data_sent} column_name={this.column_name} scroll_callback={this.callbackScroll} reset_scroll={this.reset_scroll} style={{ "height": this.state.windowHeight-44, "width": this.state.windowWidth}}>
                          {rows}
                        </StickyTable>
                      </div>
                    );

    var tableFooter = (
                        <div className="BottomTable" key="tableFooter">
                          &nbsp;
                          <div className="numberOfRows">
                            {numberWithCommas(this.size)} rows
                          </div>
                          <div className="jumpToRowContainer">
                            <input className="rowNumber" id="rowNum" onKeyDown={this.enterPressJumpRow.bind(this)} placeholder="Row #"/>
                            <img className="enterSymbol" onClick={this.rowHandler.bind(this)} src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEYAAAAxCAYAAABnCd/9AAAAAXNSR0IArs4c6QAAA9RJREFUaAXtmk1oE0EUx80mahCiglKKpSAiHrTUSz1YBL9REEE8BBSqLQrRNm1BvPSk9ODHQSHpRywKwUMvxVIQrccqanvw5qEHD4LooQgeaqGY5svfK01Yt7t1d7Mpm00Wys6+nZl9/1/fm5mdrG9DlR0DAwNn8vn8HWRP9/T03DaS7zO64UV7LBa7jq4EfwHR5/f7d0ej0W9S1h6K1uDVa6D0o+0pf8tQRCdgQnLWO4qV9G56wTYyMrIxlUo9I32uWNHjaTDxeHwrUMaBcsoKFKnr2VRKJBINAHlvB4pnwQClKZ1OzyCwWUTaOTwXMUzHJ4DygUhptAOk0MZTY8zQ0NDebDY7CZTNBYF2z56KGIC0OAFFYHoNjGN6HOvIbsi6tZ1jYwxrhqOIjBDKiz6f7zHvIbNuFW3GL0cihuX2LR42BZRLnK9x/shAeMiMA26tUxIYAChESgxxjyirX0i3MzvccKtoM37ZTqVkMhlkzTAKkIt6D8LeomevFJstMIODgzsWFhZeIr7VSCjjjK2+jfpbb7vlVBoeHt6Ty+Wm14Ky3iLK8TxLYGRAzWQyM0DZVw5n3NSnaTAMsucZUN8Cpc5NAsrliykwDLIyw0wAZUu5HHFbv2uCAYSPNcp9xpQEZb/bnC+nP4Yzx9jY2CbSJ8nDL5fTAbf2rQuGfdJtc3NzEzh93K2Ol9uvVWCYeRrZJ31D6hwo5eG0r2NsuldKH1bb8sz9VtsY1f8HDKlzcGWjZ5dRAwv2nYxNfRbqu6pqcfBlNXsa4rJ57AQUV4m048wyGKBc5b/7mg4Mf4Cy03kltwmQPu2kj8w+tUNFQCF14qrrWnGFgKRSLX10wkFheyClY696k0SMfCtSOzQEFDatHxI1NThaMHINnH6+FWkHUFpzv2oviws8vix6rijKOeD8rgYaMrYGg8EfRlrVO/vLddi6bOZH8UkuGowambHz4HnqvTJTd73rsETJkCEvCAZD/1aBESflRZItTIHTZNdpwMySoiW9iNp9thPtiqmk7qyrq+s7YXYEcVNqezWVdcEIgEgkMl9fX38WOKPVBKSg1RCMVAiHw0vd3d1tFB8UGlTLeU0wAoGIyff29vYxY92knK2B0RAgcp4A5wJwFjW3PHn534hRq5bpjWnuGHB+qu1eLFsCIwCYsT4FAoHDwPniRSAFTZbBSMPOzs6vpFUrcKYLHWnPLKJyWlslXdsCIwJJq1+hUOgkxXEDwZ8N7BVhtg1G1HV0dPxhdRumKB8PqY8loqmit0t1XwnUCs2W+Sm3DRhR6susdRdg78y2dWO9vzv+PVLOdXkdAAAAAElFTkSuQmCC" height={8}/>
                          </div>
                        </div>
                      );

      var imageContainer = (
                            <div id="image_container" key="image_container">
                              <div id="arrow_left">
                                <div id="diamond">
                                </div>
                                <div id="diamond_top">
                                </div>
                              </div>
                              <img id="image_source_container" src="" />
                              <div id="image_loading_container">
                                <div className="table_loading_parent">
                                    <div className="table_loader_container">
                                        <div className="table_loader"></div>
                                    </div>
                                </div>
                              </div>
                            </div>
                            );

      this.table_array.push(tableBody);
      this.table_array.push(tableFooter);
      this.table_array.push(imageContainer);

      var temp_table = this.table_array[0];

      for(var x = 1; x < this.table_array.length; x++){
        temp_table = [temp_table, this.table_array[x]];
      }

      var $this = this;

      this.setState({table: temp_table}, function() {
        if(callback_accordion){
            $this.y = y;
            $this.column_name = column_name;
            $this.drawTable()

            var element_index = String(parseInt(y, 10) - 1);

            if(window.navigator.platform == 'MacIntel'){
                window.webkit.messageHandlers["scriptHandler"].postMessage({status: 'getAccordion', column: column_name_str, index: element_index});
            }else{
                window.postMessageToNativeClient('{"method":"get_accordion", "column": "' + column_name_str + '", "index": ' + element_index + '}');
            }
        }
      });
  }

  updateData(data){
    this.data = data;

    this.data_sent = undefined;
    this.column_name = undefined;
    this.y = -1;

    var active_element_loop = document.getElementsByClassName("active_element");

    for(var ele = 0; ele < active_element_loop.length; ele++){
      active_element_loop[ele].children[0].children[1].children[0].style.display = "block";
      active_element_loop[ele].children[0].children[1].children[1].style.display = "none";
      active_element_loop[ele].children[0].children[1].classList.remove("active_arrow");
      active_element_loop[ele].classList.remove("active_element");
    }

    this.drawTable()
  }

  cleanImageDictionary(){
    for (var key in this.image_dictionary){
      if(parseInt(key, 10) < this.set_lower*this.step_size || parseInt(key, 10) > this.set_higher*this.step_size){
        delete this.image_dictionary[key];
      }
    }
  }

  setImageData(value){
    this.cleanImageDictionary();
    if(value.data){
      if(value.data.data){
        for(var x = 0; x < value.data.data.length; x++){
          if (!this.image_dictionary[String(value.data.data[x]["idx"])]) {
            this.image_dictionary[String(value.data.data[x]["idx"])] = {};
          }
          if (!this.image_dictionary[String(value.data.data[x]["idx"])][value.data.data[x]["column"]]) {
            this.image_dictionary[String(value.data.data[x]["idx"])][value.data.data[x]["column"]] = {};
          }
          this.image_dictionary[String(value.data.data[x]["idx"])][value.data.data[x]["column"]]["image"] = value.data.data[x]["image"];
          this.image_dictionary[String(value.data.data[x]["idx"])][value.data.data[x]["column"]]["format"] = value.data.data[x]["format"];
        }
      }
    }
  }

  render() {
    return (
      <div>
        {this.state.table}
      </div>
    );
  }
}

export default TcTable;
