



# Purpose: to write human readable format into stdf, used after  ill-formatted
#            stdf is fixed by stdf4ascii tool.

import re
import struct
from pystdf.Types import *
from pystdf import V4
# TODO: multiple lines for one value
# TODO: why perl tool has

def known_size(datatype_code):
    """
    return None if size is various, e.g. D*n
    else return the digits
    """
    m = re.search(r'(\d+)$', datatype_code)
    if m:
        return int(m.group(0))
    return None

def process_file(txt_in, stdf_out):
    """
    Read a human readable text file and write to stdf
    Expected format:
    Record header
    key1 = value1
    key2 = value2
    """

    # create a cached map to look up for
    name_to_rec_code_map = dict(
        [ ( recType.__class__.__name__.upper()  , (recType.typ, recType.sub )) for recType in V4.records ]
    )
    #print(name_to_rec_code_map)
    name_to_instance_map = dict(
        [ ( recType.__class__.__name__.upper()  , recType) for recType in V4.records ]
    )
    #print(name_to_instance_map)

    # because we need to get the bytes size of the record, we need to collect all lines
    # one each record
    one_record_content = []
    current_header_name = None


    def do_one_record(header_name, list_of_kv_tuple):
        """given the header name and lines of key/values pairs,
        to return bytes of data to be dumped into file """
        print(list_of_kv_tuple)
        # convert header into codes
        type_and_sub = name_to_rec_code_map[header_name]

        # guess the size from record instance
        inst = name_to_instance_map[header_name]
        total_size = 0
        vals = []
        for field, datatype_code in inst.fieldMap:
            est_size = known_size(datatype_code)
            if est_size:
                total_size += est_size

        for tpl in list_of_kv_tuple:
            print(tpl)
            k, v = tpl
            vals.append(v)

        print(vals)
        # dump header ( rec_len, rec_type, rec_sub )
        header = (total_size ,)
        header += type_and_sub
        print("header {}".format(header))
        values = tuple(vals)
        print("values {}".format(values))




        #s = struct.Struct()
        #packed_data = s.pack(*values)

        # ref
        #values = (1, 'ab', 2.7)
        #s = struct.Struct('I 2s f')
        #packed_data = s.pack(*values)

        #struct.Struct(code + ' I 2s f')
        #header_in_bytes = struct.pack("<" + fmt +  )
        #write_keyvalue(fout, header_in_bytes)

        print("ready to dump bytes for {}  (size: {} )".format(header_name, total_size ))
        #return packed_data


    with open(stdf_out, "wb+") as fout:
        with open(txt_in, "r") as fin:
            for line_idx, line in enumerate(fin):
                if line_idx == 0 :  #BOH
                    pass  # no handling
                else:
                    m = re.search(r'(\w+?)\s*=>\s*(.*)', line) # , re.MULTILINE
                    if m: # value line
                        # write to stdf
                        # cache key/value into content for one record processing
                        one_record_content.append((m.group(1), m.group(2)))

                    else: # header  but not <BOF>, <EOF>
                        if not line.startswith(">") and line.strip() != "" and len(line.strip()) == 3: # TODO: temp avoid valuue is multiple lines which includes carriage return char.
                            new_header_name = line.rstrip()


                             # set for first encounter
                            if not current_header_name:
                                current_header_name = new_header_name

                            # dump one record, avoid first FAR record without any kv in the one_record_content
                            if new_header_name != current_header_name:
                                bytes = do_one_record(current_header_name, one_record_content)

                            # reset to refill
                            current_header_name = new_header_name
                            one_record_content.clear()
                            print(new_header_name)



def write_header(file_out, header_in_bytes):
    """dump header to file"""
    file_out.write(header_in_bytes)

def write_keyvalue(file, key, value):
    """dump keyvalue to file"""
    pass

if __name__ == "__main__":
    sample_input = "demo.txt"
    sample_output = "demo.stdf"
    process_file(sample_input, sample_output)
    # if len(sys.argv) < 3:
    #     print("Usage: %s <stdf file>" % (sys.argv[0]))
    # else:
    #     process_file(sys.argv[1],sys.argv[1] )
