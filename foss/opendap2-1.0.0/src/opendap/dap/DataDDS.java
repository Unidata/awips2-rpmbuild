/////////////////////////////////////////////////////////////////////////////
// This file is part of the "Java-DAP" project, a Java implementation
// of the OPeNDAP Data Access Protocol.
//
// Copyright (c) 2010, OPeNDAP, Inc.
// Copyright (c) 2002,2003 OPeNDAP, Inc.
// 
// Author: James Gallagher <jgallagher@opendap.org>
// 
// All rights reserved.
// 
// Redistribution and use in source and binary forms,
// with or without modification, are permitted provided
// that the following conditions are met:
// 
// - Redistributions of source code must retain the above copyright
//   notice, this list of conditions and the following disclaimer.
// 
// - Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in the
//   documentation and/or other materials provided with the distribution.
// 
// - Neither the name of the OPeNDAP nor the names of its contributors may
//   be used to endorse or promote products derived from this software
//   without specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
// IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
// TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
// PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
// TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
/////////////////////////////////////////////////////////////////////////////

/**
 * Raytheon Updates.
 * 
 * <pre>
 * 
 * SOFTWARE HISTORY
 * 
 * Date         Ticket#    Engineer    Description
 * ------------ ---------- ----------- --------------------------
 * Apr 14, 2015 4400       dhladky      Upgraded to DAP2 with backward compatibility.
 * </pre>
 */

package opendap.dap;

import java.io.*;
import java.util.Enumeration;
import java.util.zip.DeflaterOutputStream;

/**
 * The DataDDS class extends DDS to add new methods for retrieving data from
 * the server, and printing out the contents of the data.
 *
 * @author jehamby
 * @version $Revision: 25753 $
 * @see DDS
 */
public class DataDDS extends DDS {
    /**
     * The ServerVersion returned from the open OPeNDAP connection.
     */
    private ServerVersion ver;

    /**
     * Construct the DataDDS with the given server version.
     *
     * @param ver the ServerVersion returned from the open OPeNDAP connection.
     */
    public DataDDS(ServerVersion ver) {
        super();
        this.ver = ver;
    }

    public DataDDS(ServerVersion ver, BaseTypeFactory btf) {
        super(btf);
        this.ver = ver;
    }

    /**
     * Returns the <code>ServerVersion</code> given in the constructor.
     *
     * @return the <code>ServerVersion</code> given in the constructor.
     */
    public final ServerVersion getServerVersion() {
        return ver;
    }

    /**
     * Read the data stream from the given InputStream.  In the C++ version,
     * this code was in Connect.
     *
     * @param is       the InputStream to read from
     * @param statusUI the StatusUI object to use, or null
     * @throws EOFException      if EOF is found before the variable is completely
     *                           deserialized.
     * @throws IOException       thrown on any other InputStream exception.
     * @throws DataReadException when invalid data is read, or if the user
     *                           cancels the download.
     * @throws DAP2Exception     if the OPeNDAP server returned an error.
     */
    public void readData(InputStream is, StatusUI statusUI)
            throws IOException, EOFException, DAP2Exception {

      /* ByteArrayOutputStream bout = new ByteArrayOutputStream(50 * 1000);
      copy(is, bout);
      System.out.printf(" readData size=%d %n",bout.size());
      ByteArrayInputStream bufferedIS = new ByteArrayInputStream( bout.toByteArray());  */
      //statusUI = new Counter();

        // Buffer the input stream for better performance
        BufferedInputStream bufferedIS = new BufferedInputStream(is);
        // Use a DataInputStream for deserialize
        DataInputStream dataIS = new DataInputStream(bufferedIS);

        for (Enumeration e = getVariables(); e.hasMoreElements();) {
            if (statusUI != null && statusUI.userCancelled()) throw new DataReadException("User cancelled");
            ClientIO bt = (ClientIO) e.nextElement();
          
            //System.out.printf("Deserializing: %s (%s) start = %s %n", ((BaseType)bt).getTypeName(), ((BaseType)bt).getName(), counter);
            bt.deserialize(dataIS, ver, statusUI);
        }
        //System.out.printf("Deserializing: total size = %s %n", counter);

        // notify GUI of finished download
        if (statusUI != null)
            statusUI.finished();
    }

  // debug
  private class Counter implements StatusUI {
    int counter = 0;

    public void incrementByteCount(int bytes) {
      counter += bytes;
    }

    public boolean userCancelled() {
      return false; 
    }

    public void finished() {
    }

    @Override
    public String toString() {
      return " "+ counter;
    }
  }

    //debug
    private long copy(InputStream in, OutputStream out) throws IOException {
      long totalBytesRead = 0;
      byte[] buffer = new byte[8000];
      while (true) {
        int bytesRead = in.read(buffer);
        if (bytesRead == -1) break;
        out.write(buffer, 0, bytesRead);
        totalBytesRead += bytesRead;
      }
      return totalBytesRead;
    }

    /**
     * Print the dataset just read.  In the C++ version, this code was in
     * <code>geturl</code>.
     *
     * @param pw the <code>PrintWriter</code> to use.
     */
    public void printVal(PrintWriter pw) {
        for (Enumeration e = getVariables(); e.hasMoreElements();) {
            BaseType bt = (BaseType) e.nextElement();
            bt.printVal(pw, "", true);
            pw.flush();
        }
        pw.println();
    }

    /**
     * Print the dataset using OutputStream.
     *
     * @param os the <code>OutputStream</code> to use.
     */
    public final void printVal(OutputStream os) {
        PrintWriter pw = new PrintWriter(new BufferedWriter(new OutputStreamWriter(os)));
        printVal(pw);
        pw.flush();
    }

    /**
     * Dump the dataset using externalize methods. This should create
     * a multipart Mime document with the binary representation of the
     * DDS that is currently in memory.
     *
     * @param os       the <code>OutputStream</code> to use.
     * @param compress <code>true</code> if we should compress the output.
     * @param headers  <code>true</code> if we should print HTTP headers.
     * @throws IOException thrown on any <code>OutputStream</code> exception.
     */
    public final void externalize(OutputStream os, boolean compress, boolean headers)
            throws IOException {
        // First, print headers
        if (headers) {
            PrintWriter pw = new PrintWriter(new OutputStreamWriter(os));
            pw.println("HTTP/1.0 200 OK");
            /**
             * TODO We Did a Hack here to keep the version at 2.18 as far as the
             * header checking software is concerned. Otherwise downstream
             * Shared Subscriptions would fail to serialize in DD. This will
             * continue to work because the DAP protocol information (Byte Array
             * Stream Data) is identical between versions.
             */
            pw.println("Server: " + ServerVersion.getAWIPSStandardVersion());
            pw.println("Content-type: application/octet-stream");
            pw.println("Content-Description: dods-data");
            if (compress) {
                pw.println("Content-Encoding: deflate");
            }
            pw.println();
            pw.flush();
        }

        // Buffer the output stream for better performance
        OutputStream bufferedOS;
        if (compress) {
            // need a BufferedOutputStream - 3X performance - LOOK: why ??
            bufferedOS = new BufferedOutputStream(new DeflaterOutputStream(os));
        } else {
            bufferedOS = new BufferedOutputStream(os);
        }

        // Redefine PrintWriter here, so the DDS is also compressed if necessary
        PrintWriter pw = new PrintWriter(new OutputStreamWriter(bufferedOS));
        print(pw);
        // pw.println("Data:");  // JCARON CHANGED
        pw.flush();
        bufferedOS.write("\nData:\n".getBytes()); // JCARON CHANGED
        bufferedOS.flush();

        // Use a DataOutputStream for serialize
        DataOutputStream dataOS = new DataOutputStream(bufferedOS);
        for (Enumeration e = getVariables(); e.hasMoreElements();) {
            ClientIO bt = (ClientIO) e.nextElement();
            bt.externalize(dataOS);
        }
        // Note: for DeflaterOutputStream, flush() is not sufficient to flush
        // all buffered data
        dataOS.close();
    }

    /**
     * Writes data to a <code>DataOutputStream</code>. This method is used
     * primarily by GUI clients which need to download OPeNDAP data, manipulate
     * it, and then re-save it as a binary file.
     *
     * @param sink a <code>DataOutputStream</code> to write to.
     * @throws IOException thrown on any <code>OutputStream</code>
     *                     exception.
     */
    @Override
    public void externalize(DataOutputStream sink) throws IOException {
       externalize(sink,false,false);
    }

}

