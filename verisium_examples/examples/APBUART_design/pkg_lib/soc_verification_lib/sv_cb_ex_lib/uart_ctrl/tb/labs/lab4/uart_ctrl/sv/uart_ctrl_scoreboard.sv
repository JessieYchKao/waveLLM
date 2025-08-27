/*-------------------------------------------------------------------------
File name   : uart_ctrl_scoreboard.sv
Title       : APB - UART Scoreboard
Project     :
Created     :
Description : Scoreboard for data integrity check between APB UVC and UART UVC
Notes       : 
----------------------------------------------------------------------
Copyright 2007 (c) Cadence Design Systems, Inc. All Rights Reserved.
----------------------------------------------------------------------*/

class uart_ctrl_scoreboard extends uvm_scoreboard;
  bit [7:0] data_from_apb[$] ;
  bit [7:0] data_to_apb[$] ;
  bit [7:0] temp1 ;
  bit [7:0] temp2 ;
  bit [7:0] mask ;
  bit div_en;

  `ifdef UVM_WKSHP
    bit uart_error;
    bit apb_error;
  `endif

  uart_pkg::uart_frame my_frame;
  uart_pkg::uart_config csr;

  `uvm_component_utils_begin(uart_ctrl_scoreboard)
    `uvm_field_object(my_frame, UVM_ALL_ON+UVM_HEX)
    `uvm_field_int(temp1, UVM_ALL_ON+UVM_HEX)
    `uvm_field_int(temp2, UVM_ALL_ON+UVM_HEX)
  `uvm_component_utils_end  

  `uvm_analysis_imp_decl(1)
  `uvm_analysis_imp_decl(2)

  // tlm interface used by target
  uvm_analysis_imp #(apb_pkg::apb_transfer ,uart_ctrl_scoreboard)  apb_in;
  uvm_analysis_imp1 #(uart_pkg::uart_frame ,uart_ctrl_scoreboard)  uart_in;
  uvm_analysis_imp2 #(uart_pkg::uart_frame ,uart_ctrl_scoreboard)  uart_in_tx_mon;

  function new (string name = "", uvm_component parent = null);
    super.new(name, parent);
    uart_in= new("uart_in", this);
    uart_in_tx_mon= new("uart_in_tx_mon", this);
    apb_in= new("apb_in", this);
  endfunction : new

  function void assign_csr(uart_pkg::uart_config csr_setting);
     csr = csr_setting;
  endfunction : assign_csr

  // bit masking for checking data dependin on data length
  function bit[7:0] calc_mask();
    case (csr.char_len_val)
      6: return 8'b00111111;
      7: return 8'b01111111;
      8: return 8'b11111111;
      default: return 8'hff;
    endcase
  endfunction : calc_mask

 `ifdef UVM_WKSHP
    function void pre_run ();
      super.pre_run();
      assert(std::randomize(uart_error) with {uart_error dist {1:=30,0:=70};} );
      assert(std::randomize(apb_error) with {apb_error dist {1:=30,0:=70};} );  
    endfunction : pre_run

    function void corrupt_payload (uart_pkg::uart_frame frame);
      `uvm_info("LAB", $psprintf(""), UVM_HIGH);
      frame.payload+=uart_error;    	
    endfunction : corrupt_payload

    function void corrup_data (apb_pkg::apb_transfer transfer);
      `uvm_info("LAB", $psprintf(""), UVM_HIGH);
      transfer.data+=apb_error;    	
    endfunction : corrup_data
  `endif
  
  virtual function void write1( uart_pkg::uart_frame frame );
    check_data_at_uart(frame);
  endfunction : write1

  virtual function void write2(uart_pkg::uart_frame frame );
    post_uart_data(frame);
  endfunction : write2

  virtual function void write(input apb_pkg::apb_transfer transfer );
    if ((transfer.addr == `LINE_CTRL) && (transfer.direction == apb_pkg::APB_WRITE))
      div_en = transfer.data[7];

    if (!div_en) begin
    if (transfer.addr == `TX_FIFO_REG) 
    begin
      if(transfer.direction == APB_WRITE)
      begin
        post_apb_data(transfer);
      end
      if(transfer.direction == APB_READ)
      begin
        check_data_at_apb(transfer);
      end
    end
    end
  endfunction : write

  virtual function void post_apb_data(input apb_pkg::apb_transfer transfer);
        data_from_apb.push_back(transfer.data);	
  endfunction : post_apb_data

  virtual function void check_data_at_apb(input apb_pkg::apb_transfer transfer);
    begin
     `ifdef UVM_WKSHP
        corrup_data(transfer);
     `endif
      temp2 = data_to_apb.pop_front();
      if (temp2 == transfer.data ) begin
        `uvm_info("LAB", $psprintf("####### PASS : APB RECEIVED CORRECT DATA expected = %h, received = %h", temp2, transfer.data), UVM_MEDIUM);
      end
      else
      begin
          `uvm_error(get_type_name(), $psprintf("####### FAIL : APB RECEIVED WRONG DATA from UART"))
        `uvm_info("LAB", $psprintf("expected = %h, received = %h", temp2, transfer.data), UVM_MEDIUM);
      end
    end
  endfunction : check_data_at_apb

  virtual function void check_data_at_uart(input uart_pkg::uart_frame frame);
    mask = calc_mask();
    temp1 = data_from_apb.pop_front();
    `ifdef UVM_WKSHP
        corrupt_payload (frame);
     `endif 
    if ((temp1 & mask) == frame.payload) begin
      `uvm_info("LAB", $psprintf("####### PASS : UART RECEIVED CORRECT DATA expected = %h, received = %h", (temp1 & mask), frame.payload), UVM_MEDIUM);
    end
    else
    begin
      `uvm_error(get_type_name(), $psprintf("####### FAIL : UART RECEIVED WRONG DATA"))
      `uvm_info("LAB", $psprintf("expected = %h, received = %h", temp1, frame.payload), UVM_MEDIUM);
    end
  endfunction : check_data_at_uart
                    

  virtual function void post_uart_data(input uart_pkg::uart_frame frame);
    data_to_apb.push_back(frame.payload);	
  endfunction : post_uart_data

endclass
